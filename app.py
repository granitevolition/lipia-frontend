from flask import Flask, render_template_string, request, redirect, url_for, session, flash, jsonify
import random
import string
import datetime
import re
import os
from functools import wraps

import config
from models import users_db, transactions_db, create_user_session, get_user_data, user_exists, add_transaction
from utils import humanize_text, detect_ai_content, register_user_to_backend, generate_transaction_id, format_date
from templates import html_templates
from api_client import api_client

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', config.SECRET_KEY)

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template_string(html_templates['index.html'], pricing_plans=config.pricing_plans, title="Home")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # This is actually the PIN

        # Call the API to authenticate
        success, response = api_client.login_user(username, password)
        
        if success:
            user_data = response.get('user', {})
            session['user_id'] = username
            
            # Save user data in session storage
            create_user_session(username, user_data)
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            error_msg = response if isinstance(response, str) else "Invalid credentials"
            flash(error_msg, 'error')

    return render_template_string(html_templates['login.html'], title="Login")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # This is actually the PIN
        plan_type = request.form['plan_type']
        email = request.form['email']
        phone = request.form.get('phone', None)

        # Validate PIN (4 digits)
        if not password.isdigit() or len(password) != 4:
            flash('PIN must be 4 digits', 'error')
            return render_template_string(html_templates['register.html'], pricing_plans=config.pricing_plans, title="Register")
            
        # Register with the API
        success, response = api_client.register_user(username, password, phone)
        
        if success:
            # Create a session for the user
            user_data = {
                'username': username,
                'words_remaining': 0,
                'phone_number': phone,
                'plan': plan_type,
                'payment_status': 'Pending' if plan_type != 'Free' else 'Paid',
                'created_at': datetime.datetime.now().strftime('%Y-%m-%d')
            }
            create_user_session(username, user_data)
            
            # Register with backend API
            register_user_to_backend(username, email, phone, plan_type)
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            error_msg = response if isinstance(response, str) else "Registration failed"
            flash(error_msg, 'error')

    return render_template_string(html_templates['register.html'], pricing_plans=config.pricing_plans, title="Register")


@app.route('/dashboard')
@login_required
def dashboard():
    username = session['user_id']
    
    # Get fresh user data from API
    success, response = api_client.get_user(username)
    
    if success:
        user_data = response
        create_user_session(username, user_data)  # Update session storage
    else:
        user_data = get_user_data(username)  # Fallback to session storage
    
    return render_template_string(
        html_templates['dashboard.html'], 
        user=user_data,
        plan=config.pricing_plans[user_data.get('plan', 'Free')],
        title="Dashboard"
    )


@app.route('/humanize', methods=['GET', 'POST'])
@login_required
def humanize():
    message = ""
    humanized_text = ""
    username = session['user_id']
    user_data = get_user_data(username)
    
    payment_required = user_data.get('payment_status') == 'Pending' and user_data.get('plan') != 'Free'

    if request.method == 'POST':
        original_text = request.form['original_text']
        user_type = user_data.get('plan', 'Basic')

        # Only process if payment not required or on Free plan
        if not payment_required:
            word_count = len(original_text.split())
            
            # Consume words from the user's account
            success, response = api_client.consume_words(username, word_count)
            
            if success:
                # Process the text
                humanized_text, message = humanize_text(original_text, user_type)
                
                # Refresh user data after consumption
                success, user_response = api_client.get_user(username)
                if success:
                    create_user_session(username, user_response)
            else:
                if isinstance(response, dict) and 'error' in response:
                    message = response['error']
                else:
                    message = "Failed to process: Insufficient words"
        else:
            message = "Payment required to access this feature. Please upgrade your plan."

    return render_template_string(
        html_templates['humanize.html'],
        message=message,
        humanized_text=humanized_text,
        payment_required=payment_required,
        word_limit=config.pricing_plans[user_data.get('plan', 'Free')]['word_limit'],
        title="Humanize Text"
    )


@app.route('/detect', methods=['GET', 'POST'])
@login_required
def detect():
    result = None
    message = ""
    username = session['user_id']
    user_data = get_user_data(username)
    
    payment_required = user_data.get('payment_status') == 'Pending' and user_data.get('plan') != 'Free'

    if request.method == 'POST':
        text = request.form['text']

        # Check payment status for non-free users
        if not payment_required:
            # No need to consume words for detection
            result = detect_ai_content(text)
        else:
            message = "Payment required to access this feature. Please upgrade your plan."

    return render_template_string(
        html_templates['detect.html'],
        result=result,
        message=message,
        payment_required=payment_required,
        title="Detect AI"
    )


@app.route('/account')
@login_required
def account():
    username = session['user_id']
    
    # Get fresh user data and payments from API
    success, user_response = api_client.get_user(username)
    payments_success, payments_response = api_client.get_user_payments(username)
    
    if success:
        user_data = user_response
        create_user_session(username, user_data)  # Update session storage
    else:
        user_data = get_user_data(username)  # Fallback to session storage
    
    # Format transactions for display
    user_transactions = []
    if payments_success and isinstance(payments_response, list):
        for payment in payments_response:
            payment['date'] = format_date(payment.get('timestamp', ''))
            user_transactions.append(payment)
    else:
        # Fallback to session storage
        user_transactions = [t for t in transactions_db if t.get('user_id') == username]
    
    return render_template_string(
        html_templates['account.html'], 
        user=user_data, 
        plan=config.pricing_plans[user_data.get('plan', 'Free')],
        transactions=user_transactions,
        title="Account"
    )


@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    username = session['user_id']
    user_data = get_user_data(username)
    
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        plan_type = user_data.get('plan', 'Basic')
        
        # Call the API to initiate payment
        success, response = api_client.initiate_payment(username, phone_number, plan_type.lower())
        
        if success:
            # Record the transaction in session
            transaction_id = response.get('checkout_id', generate_transaction_id())
            
            transaction_data = {
                'transaction_id': transaction_id,
                'user_id': username,
                'phone_number': phone_number,
                'amount': config.pricing_plans[plan_type]['price'],
                'subscription_type': plan_type,
                'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'Completed' if response.get('status') == 'completed' else 'Pending',
                'reference': response.get('reference', 'N/A')
            }
            add_transaction(transaction_data)
            
            # Update user payment status
            user_data['payment_status'] = 'Paid' if response.get('status') == 'completed' else 'Pending'
            create_user_session(username, user_data)
            
            # Display appropriate message
            if response.get('status') == 'completed':
                flash(f'Payment successful! Transaction ID: {transaction_id}', 'success')
            else:
                flash(f'Payment initiated. Please check your phone to complete the payment.', 'info')
            
            return redirect(url_for('account'))
        else:
            error_msg = response if isinstance(response, str) else "Payment failed"
            flash(error_msg, 'error')

    return render_template_string(
        html_templates['payment.html'],
        plan=config.pricing_plans[user_data.get('plan', 'Free')],
        title="Make Payment"
    )


@app.route('/upgrade', methods=['GET', 'POST'])
@login_required
def upgrade():
    username = session['user_id']
    user_data = get_user_data(username)
    current_plan = user_data.get('plan', 'Free')
    
    if request.method == 'POST':
        new_plan = request.form['new_plan']
        
        # Update user plan in session
        user_data['plan'] = new_plan
        user_data['payment_status'] = 'Pending'
        create_user_session(username, user_data)
        
        flash(f'Your plan has been upgraded to {new_plan}. Please make payment to activate.', 'success')
        return redirect(url_for('payment'))

    # Filter available plans (exclude current plan)
    available_plans = {k: v for k, v in config.pricing_plans.items() if k != current_plan}
    
    return render_template_string(
        html_templates['upgrade.html'], 
        current_plan={'name': current_plan, **config.pricing_plans[current_plan]},
        available_plans=available_plans,
        title="Upgrade Plan"
    )


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


# API health check endpoint
@app.route('/api-health')
def api_health():
    """Check API health"""
    success, response = api_client.health_check()
    
    return jsonify({
        'api_status': 'online' if success else 'offline',
        'details': response if success else str(response)
    })


# CSS styles
@app.route('/static/style.css')
def serve_css():
    css = """
    /* Reset and base styles */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        color: #333;
        background-color: #f9f9f9;
    }
    
    a {
        color: #0066cc;
        text-decoration: none;
    }
    
    a:hover {
        text-decoration: underline;
    }
    
    /* Layout */
    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    
    header {
        background-color: #fff;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    
    .logo a {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
    }
    
    nav ul {
        display: flex;
        list-style: none;
    }
    
    nav ul li {
        margin-left: 20px;
    }
    
    main {
        min-height: calc(100vh - 160px);
        padding: 40px 0;
    }
    
    footer {
        background-color: #333;
        color: #fff;
        padding: 20px 0;
        text-align: center;
    }
    
    /* Form styles */
    .form-group {
        margin-bottom: 20px;
    }
    
    label {
        display: block;
        margin-bottom: 5px;
        font-weight: 600;
    }
    
    input, select, textarea {
        width: 100%;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 1rem;
    }
    
    textarea {
        min-height: 150px;
        resize: vertical;
    }
    
    .form-actions {
        margin-top: 30px;
    }
    
    /* Button styles */
    .button {
        display: inline-block;
        padding: 10px 20px;
        background-color: #0066cc;
        color: #fff;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 1rem;
        text-align: center;
    }
    
    .button:hover {
        background-color: #0052a3;
        text-decoration: none;
    }
    
    .button.primary {
        background-color: #0066cc;
    }
    
    .button.secondary {
        background-color: #666;
    }
    
    /* Flash messages */
    .flash-messages {
        margin-bottom: 20px;
    }
    
    .flash {
        padding: 10px 15px;
        margin-bottom: 10px;
        border-radius: 4px;
    }
    
    .flash.success {
        background-color: #dff0d8;
        color: #3c763d;
        border: 1px solid #d6e9c6;
    }
    
    .flash.error {
        background-color: #f2dede;
        color: #a94442;
        border: 1px solid #ebccd1;
    }
    
    .flash.info {
        background-color: #d9edf7;
        color: #31708f;
        border: 1px solid #bce8f1;
    }
    
    .flash.warning {
        background-color: #fcf8e3;
        color: #8a6d3b;
        border: 1px solid #faebcc;
    }
    
    /* Hero section */
    .hero {
        text-align: center;
        padding: 60px 0;
    }
    
    .hero h1 {
        font-size: 2.5rem;
        margin-bottom: 20px;
    }
    
    .hero p {
        font-size: 1.2rem;
        margin-bottom: 30px;
    }
    
    .cta-buttons {
        display: flex;
        justify-content: center;
        gap: 20px;
    }
    
    /* Features section */
    .features {
        padding: 60px 0;
        background-color: #fff;
    }
    
    .features h2 {
        text-align: center;
        margin-bottom: 40px;
    }
    
    .feature-list {
        display: flex;
        gap: 30px;
    }
    
    .feature {
        flex: 1;
        padding: 20px;
        border-radius: 4px;
        background-color: #f9f9f9;
        text-align: center;
    }
    
    .feature h3 {
        margin-bottom: 15px;
    }
    
    /* Pricing section */
    .pricing {
        padding: 60px 0;
    }
    
    .pricing h2 {
        text-align: center;
        margin-bottom: 40px;
    }
    
    .pricing-cards {
        display: flex;
        gap: 30px;
        justify-content: center;
    }
    
    .pricing-card {
        flex: 1;
        max-width: 300px;
        padding: 30px;
        border-radius: 4px;
        background-color: #fff;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    .pricing-card h3 {
        margin-bottom: 15px;
    }
    
    .pricing-card .price {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 20px;
    }
    
    .pricing-card ul {
        margin-bottom: 30px;
        list-style: none;
    }
    
    .pricing-card ul li {
        margin-bottom: 10px;
    }
    
    /* Auth forms */
    .auth-form {
        max-width: 500px;
        margin: 0 auto;
        padding: 30px;
        background-color: #fff;
        border-radius: 4px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    .auth-form h1 {
        margin-bottom: 30px;
        text-align: center;
    }
    
    .auth-form p {
        text-align: center;
        margin-top: 20px;
    }
    
    /* Dashboard */
    .dashboard h1 {
        margin-bottom: 30px;
    }
    
    .dashboard-cards {
        display: flex;
        gap: 30px;
        margin-bottom: 40px;
    }
    
    .dashboard-card {
        flex: 1;
        padding: 30px;
        background-color: #fff;
        border-radius: 4px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    .dashboard-card h2 {
        margin-bottom: 20px;
    }
    
    .big-number {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 20px;
        color: #0066cc;
    }
    
    .action-links {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    
    .action-link {
        padding: 10px;
        background-color: #f9f9f9;
        border-radius: 4px;
        text-align: center;
    }
    
    /* Tool pages */
    .tool-page {
        max-width: 800px;
        margin: 0 auto;
    }
    
    .tool-page h1 {
        margin-bottom: 30px;
    }
    
    .tool-page p {
        margin-bottom: 20px;
    }
    
    .result-message {
        margin: 30px 0;
        padding: 15px;
        background-color: #f9f9f9;
        border-radius: 4px;
    }
    
    .result-box {
        margin-top: 30px;
        padding: 20px;
        background-color: #fff;
        border-radius: 4px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    .result-box h2 {
        margin-bottom: 20px;
    }
    
    .result-content {
        margin-bottom: 20px;
        padding: 15px;
        background-color: #f9f9f9;
        border-radius: 4px;
        white-space: pre-wrap;
    }
    
    /* Score display */
    .score-display {
        margin: 20px 0;
    }
    
    .score-bar {
        height: 40px;
        border-radius: 4px;
        overflow: hidden;
        display: flex;
    }
    
    .score-fill {
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff;
        font-weight: bold;
    }
    
    .score-fill.human {
        background-color: #0066cc;
    }
    
    .score-fill.ai {
        background-color: #cc0000;
    }
    
    /* Account page */
    .account-page h1, .account-page h2 {
        margin-bottom: 30px;
    }
    
    .account-info {
        margin-bottom: 40px;
    }
    
    .info-card {
        padding: 30px;
        background-color: #fff;
        border-radius: 4px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    .info-card p {
        margin-bottom: 15px;
    }
    
    .account-actions {
        display: flex;
        gap: 20px;
        margin-bottom: 40px;
    }
    
    /* Payment-required message */
    .payment-required {
        padding: 30px;
        background-color: #f9f9f9;
        border-radius: 4px;
        text-align: center;
        margin-bottom: 30px;
    }
    
    .payment-required p {
        margin-bottom: 20px;
    }
    
    /* Status indicators */
    .status {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    
    .status.success {
        background-color: #dff0d8;
        color: #3c763d;
    }
    
    .status.warning {
        background-color: #fcf8e3;
        color: #8a6d3b;
    }
    
    /* Tables */
    .table-container {
        overflow-x: auto;
    }
    
    .data-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .data-table th, .data-table td {
        padding: 10px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
    
    .data-table th {
        background-color: #f9f9f9;
        font-weight: 600;
    }
    
    /* Payment page */
    .payment-page, .upgrade-page {
        max-width: 600px;
        margin: 0 auto;
    }
    
    .plan-details {
        margin-bottom: 30px;
        padding: 20px;
        background-color: #f9f9f9;
        border-radius: 4px;
    }
    
    /* Plan selection */
    .current-plan {
        margin-bottom: 40px;
    }
    
    .plan-options {
        display: flex;
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .plan-option {
        flex: 1;
    }
    
    .plan-option input[type="radio"] {
        display: none;
    }
    
    .plan-option label {
        display: block;
        cursor: pointer;
    }
    
    .plan-card {
        padding: 20px;
        background-color: #fff;
        border-radius: 4px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.2s;
    }
    
    .plan-card.current {
        border: 2px solid #0066cc;
    }
    
    .plan-option input[type="radio"]:checked + label .plan-card {
        border: 2px solid #0066cc;
        transform: scale(1.05);
    }
    
    /* Analysis details */
    .analysis-details {
        margin-top: 20px;
    }
    
    .analysis-details h3 {
        margin-bottom: 15px;
    }
    
    .analysis-details ul {
        list-style: none;
    }
    
    .analysis-details ul li {
        margin-bottom: 10px;
    }
    
    /* Media queries */
    @media (max-width: 768px) {
        .header-container {
            flex-direction: column;
            padding: 10px;
        }
        
        .logo {
            margin-bottom: 10px;
        }
        
        nav ul {
            flex-wrap: wrap;
            justify-content: center;
        }
        
        nav ul li {
            margin: 5px;
        }
        
        .feature-list, .dashboard-cards, .pricing-cards {
            flex-direction: column;
        }
        
        .pricing-card {
            max-width: 100%;
        }
        
        .plan-options {
            flex-direction: column;
        }
    }
    """
    return css, 200, {'Content-Type': 'text/css'}


# JavaScript
@app.route('/static/script.js')
def serve_js():
    js = """
    // Notification close
    document.addEventListener('DOMContentLoaded', function() {
        // Add close button to flash messages
        const flashMessages = document.querySelectorAll('.flash');
        flashMessages.forEach(function(message) {
            const closeButton = document.createElement('span');
            closeButton.innerHTML = '&times;';
            closeButton.className = 'close-button';
            closeButton.style.float = 'right';
            closeButton.style.cursor = 'pointer';
            closeButton.style.marginLeft = '10px';
            closeButton.onclick = function() {
                message.style.display = 'none';
            };
            message.appendChild(closeButton);
        });
    });
    """
    return js, 200, {'Content-Type': 'text/javascript'}


if __name__ == '__main__':
    # Create a demo user for testing
    create_user_session('demo', {
        'username': 'demo',
        'words_remaining': 500,
        'phone_number': '0712345678',
        'plan': 'Basic',
        'payment_status': 'Paid',
        'created_at': datetime.datetime.now().strftime('%Y-%m-%d')
    })
    
    # Create a demo transaction
    demo_transaction = {
        'transaction_id': 'TXND3M0123456',
        'user_id': 'demo',
        'phone_number': '0712345678',
        'amount': config.pricing_plans['Basic']['price'],
        'subscription_type': 'Basic',
        'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'Completed',
        'reference': 'REF123456'
    }
    add_transaction(demo_transaction)
    
    # Start the Flask app
    print(f"Starting {config.APP_NAME} server on port {config.PORT}...")
    print(f"API URL: {config.API_URL}")
    print("\nDemo account:")
    print("  Username: demo")
    print("  Password: 1234")
    
    app.run(host='0.0.0.0', port=config.PORT, debug=config.DEBUG)
