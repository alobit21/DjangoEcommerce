from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models import Order, Stock, StockTransaction

def mark_order_processing(modeladmin, request, queryset):
    queryset.update(status='processing')
    modeladmin.message_user(request, f"{queryset.count()} orders marked as processing.", messages.SUCCESS)
mark_order_processing.short_description = "Mark selected orders as processing"

def mark_order_shipped(modeladmin, request, queryset):
    queryset.update(status='shipped')
    modeladmin.message_user(request, f"{queryset.count()} orders marked as shipped.", messages.SUCCESS)
mark_order_shipped.short_description = "Mark selected orders as shipped"

def mark_order_delivered(modeladmin, request, queryset):
    queryset.update(status='delivered')
    modeladmin.message_user(request, f"{queryset.count()} orders marked as delivered.", messages.SUCCESS)
mark_order_delivered.short_description = "Mark selected orders as delivered"

def cancel_orders(modeladmin, request, queryset):
    for order in queryset:
        if order.status != 'delivered':
            order.status = 'cancelled'
            order.save()
            
            # Return items to stock
            for item in order.orderitem_set.all():
                stock = item.product.stock
                stock.update_stock(item.quantity)
                
                # Create stock transaction
                StockTransaction.objects.create(
                    stock=stock,
                    transaction_type='in',
                    quantity=item.quantity,
                    reason=f"Order {order.order_number} cancelled",
                    created_by=request.user
                )
    
    modeladmin.message_user(request, f"{queryset.count()} orders cancelled and stock returned.", messages.SUCCESS)
cancel_orders.short_description = "Cancel selected orders and return stock"

def add_stock(modeladmin, request, queryset):
    for stock in queryset:
        # This would typically redirect to a form to specify quantity
        # For now, we'll add 10 units as an example
        quantity = 10
        stock.update_stock(quantity)
        
        StockTransaction.objects.create(
            stock=stock,
            transaction_type='in',
            quantity=quantity,
            reason="Manual stock addition via admin",
            created_by=request.user
        )
    
    modeladmin.message_user(request, f"Added 10 units to {queryset.count()} stock items.", messages.SUCCESS)
add_stock.short_description = "Add 10 units to selected stock items"

def remove_stock(modeladmin, request, queryset):
    for stock in queryset:
        # This would typically redirect to a form to specify quantity
        # For now, we'll remove 5 units as an example
        quantity = 5
        if stock.quantity >= quantity:
            stock.update_stock(-quantity)
            
            StockTransaction.objects.create(
                stock=stock,
                transaction_type='out',
                quantity=quantity,
                reason="Manual stock removal via admin",
                created_by=request.user
            )
    
    modeladmin.message_user(request, f"Removed 5 units from {queryset.count()} stock items.", messages.SUCCESS)
remove_stock.short_description = "Remove 5 units from selected stock items"
