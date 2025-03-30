import requests
import json
from datetime import datetime
import config

class LipiaClient:
    """Client for interacting with the Lipia API"""
    
    def __init__(self, base_url=None, api_key=None):
        """Initialize the client with API settings"""
        self.base_url = base_url or config.API_URL
        self.api_key = api_key or config.API_KEY
        self.timeout = 30  # Request timeout in seconds
    
    def register_user(self, username, pin, phone_number=None):
        """Register a new user"""
        try:
            payload = {
                'username': username,
                'pin': pin
            }
            
            if phone_number:
                payload['phone_number'] = phone_number
            
            response = requests.post(
                f"{self.base_url}/users/register",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 201:
                return True, response.json()
            else:
                error_msg = response.json().get('error', 'Unknown error') if response.status_code < 500 else response.text
                return False, error_msg
        except Exception as e:
            return False, str(e)
    
    def login_user(self, username, pin):
        """Login a user"""
        try:
            payload = {
                'username': username,
                'pin': pin
            }
            
            response = requests.post(
                f"{self.base_url}/users/login",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                error_msg = response.json().get('error', 'Unknown error') if response.status_code < 500 else response.text
                return False, error_msg
        except Exception as e:
            return False, str(e)
    
    def get_user(self, username):
        """Get user data"""
        try:
            response = requests.get(
                f"{self.base_url}/users/{username}",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                error_msg = response.json().get('error', 'Unknown error') if response.status_code < 500 else response.text
                return False, error_msg
        except Exception as e:
            return False, str(e)
    
    def get_user_payments(self, username):
        """Get user payments"""
        try:
            response = requests.get(
                f"{self.base_url}/users/{username}/payments",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                error_msg = response.json().get('error', 'Unknown error') if response.status_code < 500 else response.text
                return False, error_msg
        except Exception as e:
            return False, str(e)
    
    def initiate_payment(self, username, phone, plan_type='basic'):
        """Initiate a payment"""
        try:
            payload = {
                'username': username,
                'phone': phone,
                'plan_type': plan_type
            }
            
            response = requests.post(
                f"{self.base_url}/payments/initiate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code in [200, 202]:
                return True, response.json()
            else:
                error_msg = response.json().get('error', 'Unknown error') if response.status_code < 500 else response.text
                return False, error_msg
        except Exception as e:
            return False, str(e)
    
    def get_payment_status(self, checkout_id):
        """Get payment status"""
        try:
            response = requests.get(
                f"{self.base_url}/payments/{checkout_id}/status",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                error_msg = response.json().get('error', 'Unknown error') if response.status_code < 500 else response.text
                return False, error_msg
        except Exception as e:
            return False, str(e)
    
    def consume_words(self, username, words):
        """Consume words from a user's account"""
        try:
            payload = {
                'username': username,
                'words': words
            }
            
            response = requests.post(
                f"{self.base_url}/words/consume",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                error_msg = response.json().get('error', 'Unknown error') if response.status_code < 500 else response.text
                return False, error_msg
        except Exception as e:
            return False, str(e)
    
    def health_check(self):
        """Check API health"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.text
        except Exception as e:
            return False, str(e)

# Create a client instance
api_client = LipiaClient()
