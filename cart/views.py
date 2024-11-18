from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

# Import the Cart class
from .cart import Cart 

def add_to_cart(request, product_id):
    cart = Cart(request)
    cart.add(product_id)
    messages.success(request, 'Item added to cart!')
    return redirect('cart')  # Replace 'cart' with the appropriate URL name for your cart view.

def cart(request):
    cart = Cart(request)
    for item in cart:
        print(item)  # Consider logging instead of printing for production

    return render(request, 'cart/cart.html')

@login_required
def checkout(request):
    return render(request, 'cart/checkout.html')
