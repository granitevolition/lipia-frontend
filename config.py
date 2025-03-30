import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# App name
APP_NAME = os.environ.get('APP_NAME', 'Lipia Subscription Service')

# API settings
API_URL = os.environ.get('API_URL', 'http://localhost:5000/api')
API_KEY = os.environ.get('API_KEY', 'your-api-key-here')

# Pricing plans
pricing_plans = {
    "Free": {
        "price": 0,  # USD
        "word_limit": 500,
        "description": "Free tier with 500 words per round"
    },
    "Basic": {
        "price": 20,  # USD
        "word_limit": 100,
        "description": "Basic plan with 100 words per round"
    },
    "Premium": {
        "price": 50,  # USD
        "word_limit": 1000,
        "description": "Premium plan with 1000 words per round"
    }
}

# Flask settings
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
PORT = int(os.environ.get('PORT', 5001))
