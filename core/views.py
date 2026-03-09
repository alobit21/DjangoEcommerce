from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count, Sum, F
from django.shortcuts import render,redirect
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from .forms import SignUpForm
from products.models import Product,Category
from .models import Order, Stock, UserProfile
from .decorators import redirect_admin_to_dashboard
# Create your views here.
@redirect_admin_to_dashboard
def frontpage(request):
	products = Product.objects.all()[0:8]
	return render(request, 'core/frontpage.html',{'products':products})
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        
        if form.is_valid():
            user = form.save()
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
    return redirect('frontpage')

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
            'description': f'{low_stock_products} products need restocking',
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