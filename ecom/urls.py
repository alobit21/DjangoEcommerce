from django.conf import settings
from django.conf.urls.static import static
from cart.views import add_to_cart
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views
from core import views as core_views
from core import admin_views

urlpatterns = [
    # Custom admin dashboard - must come before Django admin
    path('admin/dashboard/', core_views.admin_dashboard, name='admin_dashboard'),
    
    # Admin management URLs
    path('admin/products/', admin_views.admin_product_list, name='admin_product_list'),
    path('admin/products/add/', admin_views.admin_product_add, name='admin_product_add'),
    path('admin/products/<int:product_id>/', admin_views.admin_product_detail, name='admin_product_detail'),
    path('admin/products/<int:product_id>/edit/', admin_views.admin_product_edit, name='admin_product_edit'),
    path('admin/products/export/', admin_views.admin_product_export, name='admin_product_export'),
    path('admin/orders/', admin_views.admin_order_list, name='admin_order_list'),
    path('admin/stock/', admin_views.admin_stock_list, name='admin_stock_list'),
    path('admin/categories/', admin_views.admin_category_list, name='admin_category_list'),
    path('admin/categories/add/', admin_views.admin_category_add, name='admin_category_add'),
    path('admin/categories/<int:category_id>/update/', admin_views.admin_category_update, name='admin_category_update'),
    path('admin/users/', admin_views.admin_user_list, name='admin_user_list'),
    path('admin/reports/', admin_views.admin_reports, name='admin_reports'),
    path('admin/settings/', admin_views.admin_settings, name='admin_settings'),
    
    # API endpoints for admin actions
    path('admin/stock/<int:stock_id>/update/', admin_views.update_stock, name='admin_update_stock'),
    path('admin/orders/<int:order_id>/update-status/', admin_views.update_order_status, name='admin_update_order_status'),
    
    # Django admin URLs
    path('admin/', admin.site.urls),
    
    # Core URLs
    path('', include('core.urls')),
    path('logout/', views.LogoutView.as_view(), name='logout'),  # Use built-in LogoutView
    path('product/', include('products.urls')),
    path('cart/', include('cart.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
