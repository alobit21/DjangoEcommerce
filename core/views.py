from django.contrib.auth import login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count, Sum, F
from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from .forms import SignUpForm
from products.models import Product,Category
from .models import Order, Stock, UserProfile
from .decorators import redirect_admin_to_dashboard
from django.contrib.auth import get_backends
from decouple import config
import os
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# ONLY FOR LOCAL DEV: Allow HTTP traffic for OAuth
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def get_google_flow():
    client_config = {
        "web": {
            "client_id": config("GOOGLE_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": config("GOOGLE_CLIENT_SECRET"),
            "redirect_uris": [config("GOOGLE_REDIRECT_URI")],
        }
    }
    flow = Flow.from_client_config(
        client_config,
        scopes=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]
    )
    flow.redirect_uri = config("GOOGLE_REDIRECT_URI")
    return flow

def google_login(request):
    flow = get_google_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    request.session['google_oauth_state'] = state
    # Save the PKCE code verifier in the session
    if hasattr(flow, 'code_verifier'):
        request.session['google_code_verifier'] = flow.code_verifier
    return redirect(authorization_url)

def google_callback(request):
    from django.utils.http import urlencode
    
    state = request.session.get('google_oauth_state')
    # Validate CSRF State
    if not state or state != request.GET.get('state'):
        return redirect('/login/?' + urlencode({'error': f"CSRF_Failed_State_Was_{state}"}))
        
    flow = get_google_flow()
    
    # Restore the PKCE code verifier
    code_verifier = request.session.get('google_code_verifier')
    if code_verifier:
        flow.code_verifier = code_verifier
        
    # Exchange auth code for token
    try:
        flow.fetch_token(authorization_response=request.build_absolute_uri())
    except Exception as e:
        return redirect('/login/?' + urlencode({'error': f"TokenFetchError_{str(e)}"}))
    
    credentials = flow.credentials
    request_session = google_requests.Request()
    try:
        # Verify ID token using Google's public keys
        id_info = id_token.verify_oauth2_token(
            credentials.id_token, 
            request_session, 
            config("GOOGLE_CLIENT_ID"),
            clock_skew_in_seconds=10
        )
    except ValueError as e:
        return redirect('/login/?' + urlencode({'error': f"VerifyError_{str(e)}"}))
        
    email = id_info.get('email')
    google_id = id_info.get('sub')
    name = id_info.get('name', '')
    
    # Get or Create the Django User
    user = User.objects.filter(email=email).first()
    if not user:
        user = User.objects.create_user(username=email, email=email)
        user.first_name = name.split()[0] if name else ''
        user.last_name = ' '.join(name.split()[1:]) if name and len(name.split()) > 1 else ''
        user.save()
        
    # Bind Google ID to UserProfile
    profile, created = UserProfile.objects.get_or_create(user=user)
    if not profile.google_id:
        profile.google_id = google_id
        profile.save()
        
    # Authenticate and login
    backend = get_backends()[0]
    user.backend = f'{backend.__module__}.{backend.__class__.__name__}'
    login(request, user)
    
    return redirect('home')

@redirect_admin_to_dashboard
def frontpage(request):
	products = Product.objects.all()[0:8]
	featured_products = Product.objects.filter(is_featured=True)[0:3]
	return render(request, 'core/frontpage.html', {
		'products': products,
		'featured_products': featured_products
	})
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            # Specify the backend when logging in
            backend = get_backends()[0]  # Get the first configured backend
            user.backend = f'{backend.__module__}.{backend.__class__.__name__}'
            login(request, user)  # Log the user in after signup
            return redirect('/')  # Redirect to homepage or another page
    else:
        form = SignUpForm()

    return render(request, 'core/signup.html', {'form': form})

def login_old(request):
    return render(request,'core/login.html')
def shop(request):
	categories = Category.objects.all()
	products = Product.objects.all()
	active_category = request.GET.get('category','')

	if active_category:
		products = products.filter(category__slug=active_category)


	query = request.GET.get('search', '')

	if query:
		products = products.filter(Q(name__icontains =query) | Q(description__icontains = query))

	context = {
	     'categories':categories,
	     'products':products,
	     'active_category':active_category,
	     'query': query
	}
	return render(request, 'core/shop.html',context)

def user_logout(request):
    logout(request)  # Log the user out
    # Check if user is admin and redirect accordingly
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('admin_dashboard')
    return redirect('home')

@login_required
def user_profile(request):
    """User profile view"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    context = {
        'profile': profile,
        'orders': Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    }
    
    return render(request, 'core/profile.html', context)

@login_required
def profile_update(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        country = request.POST.get('country')
        postal_code = request.POST.get('postal_code')
        
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)
            
        profile.phone = phone
        profile.address = address
        profile.city = city
        profile.country = country
        profile.postal_code = postal_code
        profile.save()
        
        from django.contrib import messages
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    return redirect('profile')

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'core/order_detail.html', {'order': order})

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get statistics
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Order statistics
    total_orders = Order.objects.count()
    new_orders_today = Order.objects.filter(created_at__date=timezone.now().date()).count()
    
    # Order status counts
    order_stats = {
        'pending': Order.objects.filter(status='pending').count(),
        'processing': Order.objects.filter(status='processing').count(),
        'shipped': Order.objects.filter(status='shipped').count(),
        'delivered': Order.objects.filter(status='delivered').count(),
        'cancelled': Order.objects.filter(status='cancelled').count(),
    }
    
    # Product statistics
    total_products = Product.objects.count()
    new_products_this_month = Product.objects.filter(created_at__gte=thirty_days_ago).count()
    
    # Stock statistics
    low_stock_products = Stock.objects.filter(quantity__lte=F('reorder_level')).select_related('product')[:5]
    low_stock_count = Stock.objects.filter(quantity__lte=F('reorder_level')).count()
    
    # User statistics
    from django.contrib.auth.models import User
    total_users = User.objects.count()
    new_users_this_month = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    
    # Recent orders
    recent_orders = Order.objects.order_by('-created_at')[:5]
    
    # Low stock products
    low_stock_items = Stock.objects.filter(quantity__lte=F('reorder_level')).select_related('product')[:5]
    
    # Top selling products
    top_products = Product.objects.annotate(
        total_sold=Count('orderitem'),
        revenue=Sum('orderitem__price')
    ).order_by('-total_sold')[:5]
    
    # Recent activity
    recent_activities = [
        {
            'title': 'New Order Received',
            'description': f'Order #{recent_orders.first().order_number if recent_orders else "N/A"}',
            'timestamp': recent_orders.first().created_at if recent_orders else timezone.now(),
            'icon': 'fa-shopping-cart'
        },
        {
            'title': 'Low Stock Alert',
            'description': f'{low_stock_count} products need restocking',
            'timestamp': timezone.now(),
            'icon': 'fa-exclamation-triangle'
        }
    ]
    
    # Sales chart data (last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    sales_data = []
    labels = []
    
    for i in range(7):
        date = seven_days_ago + timedelta(days=i)
        daily_sales = Order.objects.filter(
            created_at__date=date.date(),
            status__in=['processing', 'shipped', 'delivered']
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        labels.append(date.strftime('%a'))
        sales_data.append(float(daily_sales))
    
    # Order status chart data
    order_status_data = [
        order_stats['pending'],
        order_stats['processing'],
        order_stats['delivered'],
        order_stats['cancelled'],
    ]
    order_status_labels = ['Pending', 'Processing', 'Delivered', 'Cancelled']
    
    # Calculate total revenue
    total_revenue = Order.objects.filter(
        status__in=['processing', 'shipped', 'delivered']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    context = {
        'stats': {
            'total_orders': total_orders,
            'new_orders_today': new_orders_today,
            'total_products': total_products,
            'new_products_this_month': new_products_this_month,
            'low_stock_products': low_stock_count,
            'total_users': total_users,
            'new_users_this_month': new_users_this_month,
        },
        'order_stats': order_stats,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
        'low_stock_items': low_stock_products,
        'top_products': top_products,
        'recent_activities': recent_activities,
        'total_revenue': total_revenue,
        'sales_chart': {
            'labels': labels,
            'data': sales_data
        },
        'order_status_chart': {
            'labels': order_status_labels,
            'data': order_status_data
        }
    }
    
    return render(request, 'admin_management/dashboard.html', context)

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    return render(request, 'core/contact.html')

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'core/category_list.html', {'categories': categories})