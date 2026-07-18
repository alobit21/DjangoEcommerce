import requests
import json
import hashlib
import hmac

def test():
    client_id = "ID0ubLc8rfWFrrkr3Tz0PigSMuYthyxK"
    api_key = "SKJ0lxbD1ePo8IDglXpnTBoioRFdytEjXw4bk2UJLT"
    secret_key = "abcd123"
    
    base_url = "https://api.clickpesa.com/v1"
    endpoint = f"{base_url}/payments/mobile-money"
    
    payload = {
        'amount': 5000.0,
        'currency': 'TZS',
        'payment_method': 'MPESA',
        'phone_number': '+255712345678',
        'reference': 'TEST-ORDER-123',
        'callback_url': 'http://localhost:8000/api/payments/webhook/clickpesa/',
        'description': 'Test payment for debugging',
    }
    
    payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    checksum = hmac.new(
        secret_key.encode('utf-8'),
        payload_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
        'X-Client-Id': client_id,
        'X-Checksum': checksum,
    }
    
    response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
    print("Status:", response.status_code)
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

if __name__ == '__main__':
    test()
