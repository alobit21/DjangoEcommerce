import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')
django.setup()

from core.clickpesa_service import ClickPesaService
import uuid

def test():
    service = ClickPesaService()
    try:
        token = service.generate_token()
        print("Token generated successfully.")
        
        preview = service.preview_ussd_push(
            token=token,
            amount="1000",
            phone_number="255749380797",
            order_reference="TEST123456"
        )
        print("Preview:")
        print(preview)
        
        push = service.initiate_ussd_push(
            token=token,
            amount="1000",
            phone_number="255749380797",
            order_reference="TEST123456"
        )
        print("Push:")
        print(push)
    except Exception as e:
        print("Error:", str(e))

if __name__ == '__main__':
    test()
