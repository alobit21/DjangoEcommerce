from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile, Order, OrderItem, Stock, StockTransaction
from .admin_actions import (
    mark_order_processing, mark_order_shipped, mark_order_delivered, 
    cancel_orders, add_stock, remove_stock
)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('get_total_price',)
    fields = ('product', 'quantity', 'price', 'get_total_price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total_amount', 'created_at', 'get_total_items')
    list_filter = ('status', 'created_at', 'user')
    search_fields = ('order_number', 'user__username', 'user__email')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'get_total_items')
    inlines = [OrderItemInline]
    actions = [mark_order_processing, mark_order_shipped, mark_order_delivered, cancel_orders]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Financial', {
            'fields': ('total_amount',)
        }),
        ('Shipping', {
            'fields': ('shipping_address',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Total Items'

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'reorder_level', 'last_updated', 'is_low_stock')
    list_filter = ('last_updated', 'reorder_level')
    search_fields = ('product__name', 'product__category__name')
    readonly_fields = ('last_updated',)
    actions = [add_stock, remove_stock]
    
    fieldsets = (
        ('Product Information', {
            'fields': ('product',)
        }),
        ('Stock Information', {
            'fields': ('quantity', 'reorder_level')
        }),
        ('Timestamps', {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        }),
    )
    
    def is_low_stock(self, obj):
        return obj.is_low_stock()
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low Stock'

@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('stock', 'transaction_type', 'quantity', 'created_by', 'created_at', 'reason')
    list_filter = ('transaction_type', 'created_at', 'created_by')
    search_fields = ('stock__product__name', 'reason', 'created_by__username')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('stock', 'transaction_type', 'quantity')
        }),
        ('Details', {
            'fields': ('reason', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
