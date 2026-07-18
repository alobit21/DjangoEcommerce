import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')
django.setup()

from core.models import Payment
from core.clickpesa_service import ClickPesaService
import json

def test():
    # Get the latest processing payment
    payment = Payment.objects.filter(status=Payment.Status.PROCESSING).order_by('-created_at').first()
    if not payment:
        payment = Payment.objects.order_by('-created_at').first()
        
    print(f"Checking payment {payment.id} with ClickPesa ID: {payment.clickpesa_payment_id}")
    
    service = ClickPesaService()
    try:
        token = service.generate_token()
        import requests
        response = requests.get(
            f"https://api.clickpesa.com/v1/payments/{payment.clickpesa_payment_id}",
            headers=service._get_auth_headers(token),
            timeout=30,
        )
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)
    except Exception as e:
        print("Exception:", str(e))
    
if __name__ == '__main__':
    test()
