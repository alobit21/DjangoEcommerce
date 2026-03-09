from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

# Import the Cart class
from .cart import Cart 

def add_to_cart(request, product_id):
    cart = Cart(request)
    cart.add(product_id)
    
    if request.htmx:
        # Return the updated cart button HTML for HTMX
        from django.template.loader import render_to_string
        cart_html = render_to_string('cart/menu_cart.html', {'cart': cart}, request=request)
        return cart_html
    else:
        # Fallback for non-HTMX requests
        messages.success(request, 'Item added to cart!')
        return redirect('cart')

def cart(request):
    cart = Cart(request)
    for item in cart:
        print(item)  # Consider logging instead of printing for production

    return render(request, 'cart/cart.html')

@login_required
def checkout(request):
    return render(request, 'cart/checkout.html')
