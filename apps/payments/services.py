import requests
from django.conf import settings
import json

class PaystackService:
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
        self.base_url = 'https://api.paystack.co'
    
    def initialize_payment(self, email, amount, reference, callback_url=None):
        """Initialize payment with Paystack"""
        url = f"{self.base_url}/transaction/initialize"
        
        headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'email': email,
            'amount': amount,  # Amount in kobo
            'reference': reference,
        }
        
        if callback_url:
            data['callback_url'] = callback_url
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response_data = response.json()
            
            if response_data.get('status'):
                return response_data['data']['authorization_url']
        except Exception as e:
            print(f"Paystack initialization error: {e}")
        
        return None
    
    def verify_payment(self, reference):
        """Verify payment with Paystack"""
        url = f"{self.base_url}/transaction/verify/{reference}"
        
        headers = {
            'Authorization': f'Bearer {self.secret_key}',
        }
        
        try:
            response = requests.get(url, headers=headers)
            response_data = response.json()
            
            if response_data.get('status'):
                return response_data['data']
        except Exception as e:
            print(f"Paystack verification error: {e}")
        
        return None

class FlutterwaveService:
    def __init__(self):
        self.secret_key = settings.FLUTTERWAVE_SECRET_KEY
        self.public_key = settings.FLUTTERWAVE_PUBLIC_KEY
        self.base_url = 'https://api.flutterwave.com/v3'
    
    def initialize_payment(self, email, amount, reference, callback_url=None):
        """Initialize payment with Flutterwave"""
        url = f"{self.base_url}/payments"
        
        headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'tx_ref': reference,
            'amount': amount,
            'currency': 'NGN',
            'customer': {
                'email': email,
            },
            'redirect_url': callback_url or 'https://your-app.com/callback'
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response_data = response.json()
            
            if response_data.get('status') == 'success':
                return response_data['data']['link']
        except Exception as e:
            print(f"Flutterwave initialization error: {e}")
        
        return None