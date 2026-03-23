from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

# Import the Cart class
from .cart import Cart 

def add_to_cart(request, product_id):
    try:
        cart = Cart(request)
        cart.add(product_id)
        
        if request.headers.get('HX-Request'):
            # Return the updated cart button HTML for HTMX
            from django.template.loader import render_to_string
            from django.http import HttpResponse
            cart_html = render_to_string('cart/menu_cart.html', {'cart': cart}, request=request)
            return HttpResponse(cart_html)
        else:
            # Fallback for non-HTMX requests
            messages.success(request, 'Item added to cart!')
            return redirect('cart')
    except Exception as e:
        # Debug the error
        print(f"Error in add_to_cart: {e}")
        if request.headers.get('HX-Request'):
            return HttpResponse(f"Error: {e}", status=500)
        else:
            messages.error(request, f"Error adding to cart: {e}")
            return redirect('cart')

def update_cart(request, product_id, action):
    try:
        cart = Cart(request)
        if action == 'increment':
            cart.add(product_id, quantity=1, update_quantity=False)
        elif action == 'decrement':
            cart.add(product_id, quantity=1, update_quantity=True)
        
        if request.headers.get('HX-Request'):
            # Return the updated cart HTML
            from django.template.loader import render_to_string
            from django.http import HttpResponse
            cart_html = render_to_string('cart/partials/cart_items.html', {'cart': cart}, request=request)
            return HttpResponse(cart_html)
        else:
            return redirect('cart')
    except Exception as e:
        print(f"Error in update_cart: {e}")
        if request.headers.get('HX-Request'):
            return HttpResponse(f"Error: {e}", status=500)
        else:
            return redirect('cart')

def cart(request):
    cart = Cart(request)
    for item in cart:
        print(item)  # Consider logging instead of printing for production

    return render(request, 'cart/cart.html', {'cart': cart})

@login_required
def checkout(request):
    return render(request, 'cart/checkout.html')
