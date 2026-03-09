from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'product_count')
    list_filter = ('name',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        count = obj.product.count()
        return format_html('<span style="color: #{};">{}</span>', 
                          'green' if count > 0 else 'red', count)
    product_count.short_description = 'Products'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'get_display_price', 'created_at', 'stock_status', 'image_thumbnail')
    list_filter = ('category', 'created_at', 'price')
    search_fields = ('name', 'description', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'get_thumbnail', 'get_display_price')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'get_display_price')
        }),
        ('Media', {
            'fields': ('image', 'thumbnail', 'get_thumbnail')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def stock_status(self, obj):
        try:
            stock = obj.stock
            if stock.quantity == 0:
                return format_html('<span style="color: red;">Out of Stock</span>')
            elif stock.is_low_stock():
                return format_html('<span style="color: orange;">Low Stock ({})</span>', stock.quantity)
            else:
                return format_html('<span style="color: green;">In Stock ({})</span>', stock.quantity)
        except:
            return format_html('<span style="color: gray;">No Stock Info</span>')
    stock_status.short_description = 'Stock Status'
    
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    image_thumbnail.short_description = 'Image'
    
    def get_display_price(self, obj):
        return obj.get_display_price()
    get_display_price.short_description = 'Price (TSH)'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        from core.models import Stock
        stock, created = Stock.objects.get_or_create(product=obj)
        if created:
            stock.quantity = 0
            stock.save()