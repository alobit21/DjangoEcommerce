from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Review
from core.models import OrderItem

def product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    can_review = False
    if request.user.is_authenticated:
        # Check if user has bought the product
        can_review = OrderItem.objects.filter(order__user=request.user, product=product, order__status__in=['delivered', 'shipped', 'processing']).exists()
        # Also check if they already reviewed it
        has_reviewed = Review.objects.filter(product=product, user=request.user).exists()
        can_review = can_review and not has_reviewed
        
    return render(request, 'product/product.html', {'product': product, 'can_review': can_review})

@login_required
def add_review(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        rating = request.POST.get('rating', 5)
        content = request.POST.get('content', '')
        
        # Check if already reviewed
        if Review.objects.filter(product=product, user=request.user).exists():
            messages.error(request, "You have already reviewed this product.")
            return redirect('product', slug=product.slug)
            
        Review.objects.create(
            product=product,
            user=request.user,
            rating=int(rating),
            content=content
        )
        messages.success(request, "Your review has been added successfully!")
        return redirect('product', slug=product.slug)
    return redirect('shop')