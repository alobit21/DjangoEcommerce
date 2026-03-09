from django.contrib import admin
from django.db.models import Count, Sum, Q
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.http import JsonResponse
from .models import Order, Stock, Product, UserProfile
from products.models import Category

class AdminDashboardMixin:
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='admin_dashboard'),
            path('dashboard/stats/', self.admin_site.admin_view(self.stats_api), name='admin_stats'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        context = {
            **self.admin_site.each_context(request),
            'title': 'Admin Dashboard',
            'total_orders': Order.objects.count(),
            'pending_orders': Order.objects.filter(status='pending').count(),
            'total_products': Product.objects.count(),
            'low_stock_products': Stock.objects.filter(quantity__lte=models.F('reorder_level')).count(),
            'total_users': User.objects.count(),
            'recent_orders': Order.objects.order_by('-created_at')[:5],
            'top_categories': Category.objects.annotate(product_count=Count('product')).order_by('-product_count')[:5],
        }
        return render(request, 'admin/dashboard.html', context)
    
    def stats_api(self, request):
        from django.db import models
        
        # Order statistics
        orders_by_status = Order.objects.values('status').annotate(count=Count('id'))
        
        # Stock levels
        stock_levels = Stock.objects.aggregate(
            total_stock=Sum('quantity'),
            low_stock=Count('id', filter=Q(quantity__lte=models.F('reorder_level')))
        )
        
        # Recent sales (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_sales = Order.objects.filter(
            created_at__gte=thirty_days_ago,
            status__in=['processing', 'shipped', 'delivered']
        ).aggregate(
            total_sales=Sum('total_amount'),
            order_count=Count('id')
        )
        
        data = {
            'orders_by_status': list(orders_by_status),
            'stock_levels': stock_levels,
            'recent_sales': recent_sales,
        }
        
        return JsonResponse(data)

class CustomAdminSite(AdminDashboardMixin, admin.AdminSite):
    site_header = 'Ecommerce Admin'
    site_title = 'Ecommerce Admin Portal'
    index_title = 'Welcome to Ecommerce Admin Portal'

# Create custom admin site
custom_admin = CustomAdminSite(name='custom_admin')

# Register models with custom admin site
from django.contrib.auth.models import User
custom_admin.register(User)
custom_admin.register(UserProfile)
custom_admin.register(Order)
custom_admin.register(Stock)
custom_admin.register(Product)
custom_admin.register(Category)
