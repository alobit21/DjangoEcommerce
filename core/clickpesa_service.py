import requests
import hashlib
import hmac
import json
from decimal import Decimal
from django.conf import settings
from .models import Payment

class ClickPesaService:
    BASE_URL = "https://api.clickpesa.com/v1"

    def __init__(self):
        self.client_id = settings.CLICKPESA_CLIENT_ID
        self.api_key = settings.CLICKPESA_API_KEY
        self.secret_key = getattr(settings, 'CLICKPESA_SECRET_KEY', '')

    def initiate_mobile_money_payment(self, payment, phone_number: str, payment_method: str = "MPESA") -> dict:
        try:
            endpoint = f"{self.BASE_URL}/payments/mobile-money"
            
            # Remove '+' from phone if present, clickpesa format
            clean_phone = phone_number
            if not clean_phone.startswith('+'):
                clean_phone = f"+{clean_phone}"

            payload = {
                'amount': float(payment.amount),
                'currency': 'TZS',
                'payment_method': payment_method,
                'phone_number': clean_phone,
                'reference': f"ORDER-{payment.order.id}"[:32],
                'callback_url': getattr(settings, 'BASE_URL', 'http://localhost:8000') + '/webhook/clickpesa/',
                'description': f'Payment for order {payment.order.order_number}',
            }
            
            payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
            checksum = hmac.new(
                self.secret_key.encode('utf-8'),
                payload_str.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}',
                'X-Client-Id': self.client_id,
                'X-Checksum': checksum,
            }
            
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            
            try:
                data = response.json()
            except Exception:
                data = {"message": response.text}
                
            if response.status_code == 200 or response.status_code == 201:
                payment.clickpesa_payment_id = data.get('id')
                payment.reference_number = payload['reference']
                payment.status = Payment.Status.PROCESSING
                payment.save()
                
                payment.order.payment_status = payment.order.PaymentStatus.PENDING_PAYMENT
                payment.order.save()
                
                return {
                    'success': True,
                    'data': data,
                    'payment_id': payment.id,
                }
            else:
                error_msg = data.get('message', f"API Error: {response.status_code}")
                payment.status = Payment.Status.FAILED
                payment.failure_reason = error_msg
                payment.save()
                
                return {
                    'success': False,
                    'error': error_msg,
                    'payment_id': payment.id,
                }
                
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            payment.status = Payment.Status.FAILED
            payment.failure_reason = error_msg
            payment.save()

            return {
                'success': False,
                'error': error_msg,
                'payment_id': payment.id,
            }