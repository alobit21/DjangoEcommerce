from django.conf import settings
from django.conf.urls.static import static
from cart.views import add_to_cart
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views
from core import views as core_views
from core import admin_views

urlpatterns = [
    # Custom admin dashboard
    path('dashboard/', core_views.admin_dashboard, name='admin_dashboard'),
    
    # Admin management URLs
    path('dashboard/products/', admin_views.admin_product_list, name='admin_product_list'),
    path('dashboard/products/add/', admin_views.admin_product_add, name='admin_product_add'),
    path('dashboard/products/<slug:product_slug>/', admin_views.admin_product_detail, name='admin_product_detail'),
    path('dashboard/products/<slug:product_slug>/edit/', admin_views.admin_product_edit, name='admin_product_edit'),
    path('dashboard/products/<slug:product_slug>/delete/', admin_views.admin_product_delete, name='admin_product_delete'),
    path('dashboard/products/<slug:product_slug>/update-stock/', admin_views.update_stock_by_slug, name='admin_update_stock_by_slug'),
    path('dashboard/products/export/', admin_views.admin_product_export, name='admin_product_export'),
    path('dashboard/orders/', admin_views.admin_order_list, name='admin_order_list'),
    path('dashboard/stock/', admin_views.admin_stock_list, name='admin_stock_list'),
    path('dashboard/categories/', admin_views.admin_category_list, name='admin_category_list'),
    path('dashboard/categories/add/', admin_views.admin_category_add, name='admin_category_add'),
    path('dashboard/categories/<int:category_id>/update/', admin_views.admin_category_update, name='admin_category_update'),
    path('dashboard/categories/<int:category_id>/delete/', admin_views.admin_category_delete, name='admin_category_delete'),
    path('dashboard/users/', admin_views.admin_user_list, name='admin_user_list'),
    path('dashboard/reports/', admin_views.admin_reports, name='admin_reports'),
    path('dashboard/settings/', admin_views.admin_settings, name='admin_settings'),
    
    # API endpoints for admin actions
    path('dashboard/stock/<int:stock_id>/update/', admin_views.update_stock, name='admin_update_stock'),
    path('dashboard/orders/<int:order_id>/update-status/', admin_views.update_order_status, name='admin_update_order_status'),
    
    # Django admin URLs
    path('admin/', admin.site.urls),
    
    # Core URLs
    path('', include('core.urls')),
    path('logout/', views.LogoutView.as_view(), name='logout'),  # Use built-in LogoutView
    path('product/', include('products.urls')),
    path('cart/', include('cart.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
