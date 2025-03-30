import random
import string
import re
from datetime import datetime
import requests
import json
import os

from api_client import api_client
import config

def humanize_text(text, user_type="Basic"):
    """
    Call the humanizer API to transform AI text into more human-like text.
    
    Args:
        text (str): The text to humanize
        user_type (str): The user's plan type
        
    Returns:
        tuple: (humanized_text, message)
    """
    # This is a placeholder - in a real implementation you'd call your actual text humanization API
    try:
        # Simulate a response
        words = text.split()
        word_count = len(words)
        
        # Truncate if over limit based on plan
        limit = 1000 if user_type == "Premium" else 100 if user_type == "Basic" else 500
        truncated = False
        message = "Text successfully humanized!"
        
        if word_count > limit:
            words = words[:limit]
            truncated = True
            message = f"Text was truncated to {limit} words due to your plan limit."
        
        # Simulated humanization by making small changes
        humanized_text = text
        humanized_text = humanized_text.replace("In conclusion", "To sum up")
        humanized_text = humanized_text.replace("It is important to note", "Keep in mind")
        humanized_text = humanized_text.replace("In this essay", "Here")
        
        if truncated:
            humanized_text = " ".join(words)
            
        return humanized_text, message
                
    except Exception as e:
        return "", f"Error: {str(e)}"

def detect_ai_content(text):
    """
    Analyze text to determine if it's likely AI-generated.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        dict: Detection results
    """
    try:
        # Simulated detection
        # In a real implementation, you would call your actual AI detection API
        text_length = len(text)
        
        # Generate some simulated scores
        formality_score = random.randint(60, 95)
        repetition_score = random.randint(40, 90)
        uniformity_score = random.randint(50, 95)
        
        # Calculate AI score
        ai_score = int((formality_score + repetition_score + uniformity_score) / 3)
        human_score = 100 - ai_score
        
        return {
            "ai_score": ai_score,
            "human_score": human_score,
            "analysis": {
                "formal_language": formality_score,
                "repetitive_patterns": repetition_score,
                "sentence_uniformity": uniformity_score
            }
        }
    except Exception as e:
        return None

def register_user_to_backend(username, email, phone=None, plan_type=None):
    """
    Register a user to the backend API
    
    Args:
        username (str): Username
        email (str): User's email
        phone (str, optional): Phone number
        plan_type (str, optional): Subscription plan
        
    Returns:
        tuple: (success, message)
    """
    try:
        success, response = api_client.register_user(username, "1234", phone)
        if success:
            return True, "Registration successful!"
        else:
            return False, f"Registration failed: {response}"
    except Exception as e:
        return False, f"Error registering user: {str(e)}"

def validate_email(email):
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    # Simple validation for demonstration
    # In a real implementation, you would have more robust validation
    return phone and len(phone) >= 10 and phone.replace('+', '').isdigit()

def format_date(date_str):
    """Format date string for display"""
    if not date_str:
        return ""
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return date_obj.strftime('%b %d, %Y %I:%M %p')
    except ValueError:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%b %d, %Y')
        except ValueError:
            return date_str

def generate_transaction_id():
    """Generate a random transaction ID"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
