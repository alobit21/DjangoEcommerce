from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q, Count, Sum, F
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
import json
from django.contrib import messages

from products.models import Product, Category
from .models import Order, OrderItem, Stock, StockTransaction, UserProfile

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@login_required
@user_passes_test(is_admin)
def admin_product_list(request):
    search = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    stock_status = request.GET.get('stock_status', '')
    
    products = Product.objects.select_related('category', 'stock').all()
    
    if search:
        products = products.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search) |
            Q(category__name__icontains=search)
        )
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if stock_status:
        if stock_status == 'in_stock':
            products = products.filter(stock__quantity__gt=F('stock__reorder_level'))
        elif stock_status == 'low_stock':
            products = products.filter(stock__quantity__lte=F('stock__reorder_level'), stock__quantity__gt=0)
        elif stock_status == 'out_of_stock':
            products = products.filter(stock__quantity=0)
    
    # Pagination
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'products': page_obj,
        'categories': categories,
        'search': search,
        'selected_category': category_id,
        'stock_status': stock_status,
    }
    
    return render(request, 'admin_management/product_list.html', context)

@login_required
@user_passes_test(is_admin)
def admin_product_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        stock_quantity = request.POST.get('stock_quantity', 0)
        reorder_level = request.POST.get('reorder_level', 10)
        
        try:
            # Create product
            product = Product.objects.create(
                name=name,
                description=description,
                price=float(price),
                category_id=category_id
            )
            
            # Create stock record
            Stock.objects.create(
                product=product,
                quantity=int(stock_quantity),
                reorder_level=int(reorder_level)
            )
            
            messages.success(request, f'Product "{name}" added successfully!')
            return redirect('admin_product_list')
            
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
    
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'title': 'Add Product'
    }
    return render(request, 'admin_management/product_form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    stock = get_object_or_404(Stock, product=product)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        stock_quantity = request.POST.get('stock_quantity', 0)
        reorder_level = request.POST.get('reorder_level', 10)
        
        try:
            # Update product
            product.name = name
            product.description = description
            product.price = float(price)
            product.category_id = category_id
            product.save()
            
            # Update stock
            stock.quantity = int(stock_quantity)
            stock.reorder_level = int(reorder_level)
            stock.save()
            
            messages.success(request, f'Product "{name}" updated successfully!')
            return redirect('admin_product_list')
            
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
    
    categories = Category.objects.all()
    context = {
        'product': product,
        'stock': stock,
        'categories': categories,
        'title': 'Edit Product'
    }
    return render(request, 'admin_management/product_form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    stock = get_object_or_404(Stock, product=product)
    
    # Get sales data for this product
    sales_data = OrderItem.objects.filter(
        product=product,
        order__status__in=['processing', 'shipped', 'delivered']
    ).aggregate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('price'),
        recent_orders=Count('order')
    )
    
    # Recent orders containing this product
    recent_orders = OrderItem.objects.filter(
        product=product
    ).select_related('order', 'order__user').order_by('-order__created_at')[:10]
    
    context = {
        'product': product,
        'stock': stock,
        'sales_data': sales_data,
        'recent_orders': recent_orders,
        'title': f'Product Details - {product.name}'
    }
    
    return render(request, 'admin_management/product_detail.html', context)

@login_required
@user_passes_test(is_admin)
def admin_product_export(request):
    import csv
    from django.http import HttpResponse
    
    # Get products with filters applied
    search = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    stock_status = request.GET.get('stock_status', '')
    
    products = Product.objects.select_related('category', 'stock').all()
    
    if search:
        products = products.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search) |
            Q(category__name__icontains=search)
        )
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if stock_status:
        if stock_status == 'in_stock':
            products = products.filter(stock__quantity__gt=F('stock__reorder_level'))
        elif stock_status == 'low_stock':
            products = products.filter(stock__quantity__lte=F('stock__reorder_level'), stock__quantity__gt=0)
        elif stock_status == 'out_of_stock':
            products = products.filter(stock__quantity=0)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Name', 'Description', 'Category', 'Price (TSH)', 
        'Stock Quantity', 'Reorder Level', 'Status', 'Created Date'
    ])
    
    for product in products:
        stock = product.stock
        if stock.quantity == 0:
            status = 'Out of Stock'
        elif stock.quantity <= stock.reorder_level:
            status = 'Low Stock'
        else:
            status = 'In Stock'
            
        writer.writerow([
            product.id,
            product.name,
            product.description,
            product.category.name if product.category else '',
            product.price,
            stock.quantity,
            stock.reorder_level,
            status,
            product.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response

@login_required
@user_passes_test(is_admin)
def admin_order_list(request):
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    orders = Order.objects.select_related('user').order_by('-created_at')
    
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    order_stats = {
        'pending': orders.filter(status='pending').count(),
        'processing': orders.filter(status='processing').count(),
        'shipped': orders.filter(status='shipped').count(),
        'delivered': orders.filter(status='delivered').count(),
        'cancelled': orders.filter(status='cancelled').count(),
    }
    
    total_revenue = orders.filter(
        status__in=['processing', 'shipped', 'delivered']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    context = {
        'orders': page_obj,
        'order_stats': order_stats,
        'total_revenue': total_revenue,
        'search': search,
        'status': status_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'admin_management/order_list.html', context)

@login_required
@user_passes_test(is_admin)
def admin_stock_list(request):
    search = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    stock_status = request.GET.get('stock_status', '')
    
    stocks = Stock.objects.select_related('product', 'product__category').all()
    
    if search:
        stocks = stocks.filter(
            Q(product__name__icontains=search) |
            Q(product__category__name__icontains=search)
        )
    
    if category_id:
        stocks = stocks.filter(product__category_id=category_id)
    
    if stock_status:
        if stock_status == 'in_stock':
            stocks = stocks.filter(quantity__gt=F('reorder_level'))
        elif stock_status == 'low_stock':
            stocks = stocks.filter(quantity__lte=F('reorder_level'), quantity__gt=0)
        elif stock_status == 'out_of_stock':
            stocks = stocks.filter(quantity=0)
    
    # Pagination
    paginator = Paginator(stocks, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    # Statistics
    stock_stats = {
        'total_products': Stock.objects.count(),
        'in_stock': Stock.objects.filter(quantity__gt=F('reorder_level')).count(),
        'low_stock': Stock.objects.filter(quantity__lte=F('reorder_level'), quantity__gt=0).count(),
        'out_of_stock': Stock.objects.filter(quantity=0).count(),
    }
    
    low_stock_items = Stock.objects.filter(
        quantity__lte=F('reorder_level')
    ).select_related('product')[:10]
    
    # Add needed stock calculation to each stock item
    for stock in low_stock_items:
        stock.needed_stock = max(0, (stock.reorder_level + 10) - stock.quantity)
    
    context = {
        'stocks': page_obj,
        'categories': categories,
        'stock_stats': stock_stats,
        'low_stock_items': low_stock_items,
        'search': search,
        'selected_category': category_id,
        'stock_status': stock_status,
    }
    
    return render(request, 'admin_management/stock_list.html', context)

@login_required
@user_passes_test(is_admin)
def admin_category_list(request):
    categories = Category.objects.annotate(product_count=Count('product')).order_by('name')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'admin_management/category_list.html', context)

@login_required
@user_passes_test(is_admin)
def admin_category_add(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            slug = data.get('slug')
            
            if not name or not slug:
                return JsonResponse({'success': False, 'message': 'Name and slug are required'}, status=400)
            
            category = Category.objects.create(
                name=name,
                slug=slug
            )
            return JsonResponse({'success': True, 'message': 'Category added successfully'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)

@login_required
@user_passes_test(is_admin)
def admin_category_update(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            slug = data.get('slug')
            
            if not name or not slug:
                return JsonResponse({'success': False, 'message': 'Name and slug are required'}, status=400)
            
            category.name = name
            category.slug = slug
            category.save()
            return JsonResponse({'success': True, 'message': 'Category updated successfully'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)

@login_required
@user_passes_test(is_admin)
def admin_user_list(request):
    search = request.GET.get('search', '')
    
    users = User.objects.all().order_by('-date_joined')
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'search': search,
    }
    
    return render(request, 'admin_management/user_list.html', context)

@require_POST
@login_required
@user_passes_test(is_admin)
def update_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    
    try:
        data = json.loads(request.body)
        quantity = data.get('quantity', 0)
        transaction_type = data.get('transaction_type', 'adjustment')
        reason = data.get('reason', '')
        
        # Update stock
        old_quantity = stock.quantity
        stock.quantity += quantity
        stock.save()
        
        # Create transaction record
        StockTransaction.objects.create(
            stock=stock,
            transaction_type=transaction_type,
            quantity=abs(quantity),
            reason=reason,
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Stock updated successfully. New quantity: {stock.quantity}'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@require_POST
@login_required
@user_passes_test(is_admin)
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        
        old_status = order.status
        order.status = new_status
        order.save()
        
        # If order is cancelled, return items to stock
        if new_status == 'cancelled' and old_status != 'cancelled':
            for item in order.orderitem_set.all():
                stock = item.product.stock
                stock.quantity += item.quantity
                stock.save()
                
                StockTransaction.objects.create(
                    stock=stock,
                    transaction_type='in',
                    quantity=item.quantity,
                    reason=f'Order {order.order_number} cancelled',
                    created_by=request.user
                )
        
        return JsonResponse({
            'success': True,
            'message': f'Order status updated to {new_status}'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@user_passes_test(is_admin)
def admin_reports(request):
    # Get date range from request
    date_from = request.GET.get('date_from', (timezone.now() - timedelta(days=30)).date())
    date_to = request.GET.get('date_to', timezone.now().date())
    
    # Sales data
    orders = Order.objects.filter(
        created_at__date__gte=date_from,
        created_at__date__lte=date_to
    )
    
    # Sales by category
    sales_by_category = OrderItem.objects.filter(
        order__created_at__date__gte=date_from,
        order__created_at__date__lte=date_to
    ).values('product__category__name').annotate(
        total_sales=Sum('price'),
        quantity=Sum('quantity')
    ).order_by('-total_sales')
    
    # Top products
    top_products = OrderItem.objects.filter(
        order__created_at__date__gte=date_from,
        order__created_at__date__lte=date_to
    ).values('product__name').annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('price')
    ).order_by('-total_quantity')[:10]
    
    # Order status breakdown
    order_status_data = orders.values('status').annotate(count=Count('id'))
    
    # Extract labels and counts for chart
    order_status_labels = [item['status'] for item in order_status_data]
    order_status_counts = [item['count'] for item in order_status_data]
    
    # Daily sales
    daily_sales = []
    dates = []
    current_date = date_from
    while current_date <= date_to:
        daily_total = orders.filter(created_at__date=current_date).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        daily_sales.append(float(daily_total))
        dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'total_orders': orders.count(),
        'total_revenue': orders.aggregate(total=Sum('total_amount'))['total'] or 0,
        'sales_by_category': sales_by_category,
        'top_products': top_products,
        'order_status_data': order_status_data,
        'order_status_labels': order_status_labels,
        'order_status_counts': order_status_counts,
        'daily_sales': daily_sales,
        'dates': dates,
    }
    
    return render(request, 'admin_management/reports.html', context)

@login_required
@user_passes_test(is_admin)
def admin_settings(request):
    if request.method == 'POST':
        # Handle settings update
        site_name = request.POST.get('site_name', 'Ecommerce Store')
        admin_email = request.POST.get('admin_email', 'admin@example.com')
        low_stock_threshold = request.POST.get('low_stock_threshold', 10)
        
        # Here you would typically save these to a settings model or file
        # For now, we'll just show a success message
        from django.contrib import messages
        messages.success(request, 'Settings updated successfully!')
        
        return redirect('admin_settings')
    
    # Get current settings (placeholder values)
    context = {
        'site_name': 'Ecommerce Store',
        'admin_email': 'admin@example.com',
        'low_stock_threshold': 10,
        'django_version': '5.0.7',
        'python_version': '3.12.3',
    }
    
    return render(request, 'admin_management/settings.html', context)
