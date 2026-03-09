from django.conf import settings
from products.models import Product

class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def __iter__(self):
        # Create a copy of cart items with product objects for iteration
        cart_items = []
        for product_id in self.cart.keys():
            product = Product.objects.get(pk=product_id)
            cart_item = self.cart[str(product_id)].copy()
            cart_item['product'] = product
            cart_item['total_price'] = int(product.price * cart_item['quantity']) / 100
            cart_items.append(cart_item)
        
        for item in cart_items:
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def add(self, product_id, quantity=1, update_quantity=False):
        product_id = str(product_id)

        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'id': product_id}

        if update_quantity:
            self.cart[product_id]['quantity'] += int(quantity)

            if self.cart[product_id]['quantity'] <= 0:
                self.remove(product_id)
        else:
            self.cart[product_id]['quantity'] += 1

        self.save()

    def remove(self, product_id):
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def get_total_cost(self):
        total_cost = 0
        for product_id in self.cart.keys():
            product = Product.objects.get(pk=product_id)
            total_cost += product.price * self.cart[str(product_id)]['quantity']
        return total_cost
