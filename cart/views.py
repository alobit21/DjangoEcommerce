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
            cart.add(product_id, quantity=1, update_quantity=True)
        elif action == 'decrement':
            cart.add(product_id, quantity=-1, update_quantity=True)
        elif action == 'remove':
            cart.remove(product_id)
        
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

from core.models import Order, OrderItem, Payment
from core.clickpesa_service import ClickPesaService
import uuid

@login_required
def checkout(request):
    cart = Cart(request)
    
    if len(cart) == 0:
        messages.error(request, "Your cart is empty.")
        return redirect('shop')
        
    if request.method == 'POST':
        # Get data from request.POST
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        zip_code = request.POST.get('zip_code')
        city = request.POST.get('city')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        # We enforce clickpesa for now
        payment_method = request.POST.get('payment_method', 'clickpesa')
        
        full_address = f"{address}, {city}, {zip_code}"
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            order_number=str(uuid.uuid4())[:10].upper(),
            total_amount=cart.get_total_cost(),
            shipping_address=full_address
        )
        
        # Create order items
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity']
            )
            
        # Create Payment
        payment = Payment.objects.create(
            order=order,
            amount=order.total_amount,
            currency='TZS',
            phone_number=phone,
            channel=payment_method
        )
        
        # Initiate ClickPesa Payment
        payment_phone = request.POST.get('payment_phone')
        clean_phone = payment_phone.replace('+', '').strip() if payment_phone else phone.replace('+', '').strip()
        if clean_phone.startswith('0'):
            clean_phone = '255' + clean_phone[1:]
        
        # Deduce network
        prefix = clean_phone[3:5] if clean_phone.startswith('255') else clean_phone[0:2]
        if prefix in ['74', '75', '76']:
            network = 'MPESA'
        elif prefix in ['71', '65', '67', '77']:
            network = 'TIGO_PESA'
        elif prefix in ['78', '68', '69', '79']:
            network = 'AIRTEL_MONEY'
        elif prefix in ['62']:
            network = 'HALOPESA'
        else:
            network = 'MPESA' # fallback
            
        clickpesa = ClickPesaService()
        result = clickpesa.initiate_mobile_money_payment(payment, clean_phone, network)
        
        if result['success']:
            messages.success(request, 'Payment initiated! Please check your phone to approve the USSD push.')
            cart.clear()
            return redirect('frontpage')
        else:
            messages.error(request, f"Payment failed: {result.get('error')}")
            return redirect('checkout')
            
    return render(request, 'cart/checkout.html', {'cart': cart})
