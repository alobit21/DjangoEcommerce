import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')
django.setup()

from core.clickpesa_service import ClickPesaService
from core.models import Order, Payment
from django.contrib.auth.models import User

def test():
    try:
        user = User.objects.first()
        import uuid
        order = Order.objects.create(
            user=user,
            order_number=str(uuid.uuid4())[:10],
            total_amount=5000,
            shipping_address="Test Address"
        )
        payment = Payment.objects.create(
            order=order,
            amount=order.total_amount,
            currency='TZS',
            phone_number="+255749380797",
            channel="MPESA"
        )
        
        service = ClickPesaService()
        result = service.initiate_mobile_money_payment(payment, "255749380797", "MPESA")
        
        result['payment_id'] = str(result.get('payment_id', ''))
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print("Error:", str(e))

if __name__ == '__main__':
    test()
