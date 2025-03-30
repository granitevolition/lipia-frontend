# HTML templates for the Lipia application

# Base layout with navigation and common elements
base_layout = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Lipia Subscription Service</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <header>
        <div class="header-container">
            <div class="logo">
                <a href="{{ url_for('index') }}">Lipia Subscription Service</a>
            </div>
            <nav>
                <ul>
                    {% if 'user_id' in session %}
                        <li><a href="{{ url_for('dashboard') }}">Dashboard</a></li>
                        <li><a href="{{ url_for('humanize') }}">Humanize Text</a></li>
                        <li><a href="{{ url_for('detect') }}">Detect AI</a></li>
                        <li><a href="{{ url_for('account') }}">Account</a></li>
                        <li><a href="{{ url_for('logout') }}">Logout</a></li>
                    {% else %}
                        <li><a href="{{ url_for('index') }}">Home</a></li>
                        <li><a href="{{ url_for('login') }}">Login</a></li>
                        <li><a href="{{ url_for('register') }}">Register</a></li>
                    {% endif %}
                </ul>
            </nav>
        </div>
    </header>
    
    <main>
        <div class="container">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    <div class="flash-messages">
                        {% for category, message in messages %}
                            <div class="flash {{ category }}">{{ message }}</div>
                        {% endfor %}
                    </div>
                {% endif %}
            {% endwith %}
            
            {% block content %}{% endblock %}
        </div>
    </main>
    
    <footer>
        <div class="container">
            <p>&copy; 2025 Lipia Subscription Service. All rights reserved.</p>
        </div>
    </footer>
    
    <script src="{{ url_for('static', filename='script.js') }}"></script>
</body>
</html>
"""

# Index page
index_template = """
{% extends "base.html" %}

{% block content %}
<section class="hero">
    <h1>Welcome to Lipia Subscription Service</h1>
    <p>The easiest way to manage your subscription payments</p>
    
    <div class="cta-buttons">
        <a href="{{ url_for('register') }}" class="button primary">Get Started</a>
        <a href="{{ url_for('login') }}" class="button secondary">Login</a>
    </div>
</section>

<section class="features">
    <h2>What We Offer</h2>
    
    <div class="feature-list">
        <div class="feature">
            <h3>Text Humanization</h3>
            <p>Transform AI-generated text into human-like content</p>
        </div>
        
        <div class="feature">
            <h3>AI Detection</h3>
            <p>Check if content was written by AI or a human</p>
        </div>
        
        <div class="feature">
            <h3>Flexible Subscriptions</h3>
            <p>Choose a plan that fits your needs and budget</p>
        </div>
    </div>
</section>

<section class="pricing">
    <h2>Pricing Plans</h2>
    
    <div class="pricing-cards">
        {% for name, plan in pricing_plans.items() %}
        <div class="pricing-card">
            <h3>{{ name }}</h3>
            <div class="price">${{ plan.price }}</div>
            <ul>
                <li>{{ plan.word_limit }} words per round</li>
                <li>{{ plan.description }}</li>
            </ul>
            <a href="{{ url_for('register') }}" class="button">Sign Up</a>
        </div>
        {% endfor %}
    </div>
</section>
{% endblock %}
"""

# Login page
login_template = """
{% extends "base.html" %}

{% block content %}
<section class="auth-form">
    <h1>Login to Your Account</h1>
    
    <form method="post" action="{{ url_for('login') }}">
        <div class="form-group">
            <label for="username">Username</label>
            <input type="text" id="username" name="username" required>
        </div>
        
        <div class="form-group">
            <label for="password">PIN</label>
            <input type="password" id="password" name="password" required>
        </div>
        
        <div class="form-actions">
            <button type="submit" class="button primary">Login</button>
            <p>Don't have an account? <a href="{{ url_for('register') }}">Register</a></p>
        </div>
    </form>
</section>
{% endblock %}
"""

# Registration page
register_template = """
{% extends "base.html" %}

{% block content %}
<section class="auth-form">
    <h1>Create an Account</h1>
    
    <form method="post" action="{{ url_for('register') }}">
        <div class="form-group">
            <label for="username">Username</label>
            <input type="text" id="username" name="username" required>
        </div>
        
        <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" name="email" required>
        </div>
        
        <div class="form-group">
            <label for="phone">Phone Number (07XXXXXXXX)</label>
            <input type="tel" id="phone" name="phone" pattern="[0-9]{10}" placeholder="0712345678" required>
        </div>
        
        <div class="form-group">
            <label for="password">PIN (4 digits)</label>
            <input type="password" id="password" name="password" pattern="[0-9]{4}" maxlength="4" required>
        </div>
        
        <div class="form-group">
            <label for="plan_type">Subscription Plan</label>
            <select id="plan_type" name="plan_type" required>
                {% for name, plan in pricing_plans.items() %}
                <option value="{{ name }}">{{ name }} (${{ plan.price }}) - {{ plan.word_limit }} words</option>
                {% endfor %}
            </select>
        </div>
        
        <div class="form-actions">
            <button type="submit" class="button primary">Register</button>
            <p>Already have an account? <a href="{{ url_for('login') }}">Login</a></p>
        </div>
    </form>
</section>
{% endblock %}
"""

# Dashboard page
dashboard_template = """
{% extends "base.html" %}

{% block content %}
<section class="dashboard">
    <h1>Welcome, {{ user.username }}</h1>
    
    <div class="dashboard-cards">
        <div class="dashboard-card">
            <h2>Words Remaining</h2>
            <div class="big-number">{{ user.words_remaining }}</div>
            <p>Your plan: {{ plan.description }}</p>
            <a href="{{ url_for('humanize') }}" class="button">Humanize Text</a>
        </div>
        
        <div class="dashboard-card">
            <h2>Quick Actions</h2>
            <div class="action-links">
                <a href="{{ url_for('humanize') }}" class="action-link">Humanize Text</a>
                <a href="{{ url_for('detect') }}" class="action-link">Detect AI</a>
                <a href="{{ url_for('account') }}" class="action-link">Manage Account</a>
                <a href="{{ url_for('payment') }}" class="action-link">Make Payment</a>
            </div>
        </div>
    </div>
</section>
{% endblock %}
"""

# Humanize text page
humanize_template = """
{% extends "base.html" %}

{% block content %}
<section class="tool-page">
    <h1>Humanize Text</h1>
    
    {% if payment_required %}
    <div class="payment-required">
        <p>Payment required to access this feature. Please upgrade your plan.</p>
        <a href="{{ url_for('payment') }}" class="button">Make Payment</a>
    </div>
    {% else %}
    <p>Paste AI-generated text below to make it sound more human-like.</p>
    <p>Words remaining: {{ word_limit }}</p>
    
    <form method="post" action="{{ url_for('humanize') }}">
        <div class="form-group">
            <label for="original_text">Original Text</label>
            <textarea id="original_text" name="original_text" rows="10" required></textarea>
        </div>
        
        <div class="form-actions">
            <button type="submit" class="button primary">Humanize</button>
        </div>
    </form>
    
    {% if message %}
    <div class="result-message">
        <p>{{ message }}</p>
    </div>
    {% endif %}
    
    {% if humanized_text %}
    <div class="result-box">
        <h2>Humanized Text</h2>
        <div class="result-content">
            <p>{{ humanized_text }}</p>
        </div>
        <button class="button" onclick="copyText()">Copy to Clipboard</button>
    </div>
    {% endif %}
    {% endif %}
</section>

<script>
function copyText() {
    const text = document.querySelector('.result-content').innerText;
    navigator.clipboard.writeText(text).then(() => {
        alert('Text copied to clipboard!');
    });
}
</script>
{% endblock %}
"""

# Detect AI page
detect_template = """
{% extends "base.html" %}

{% block content %}
<section class="tool-page">
    <h1>Detect AI Content</h1>
    
    {% if payment_required %}
    <div class="payment-required">
        <p>Payment required to access this feature. Please upgrade your plan.</p>
        <a href="{{ url_for('payment') }}" class="button">Make Payment</a>
    </div>
    {% else %}
    <p>Paste text below to analyze whether it was written by AI or a human.</p>
    
    <form method="post" action="{{ url_for('detect') }}">
        <div class="form-group">
            <label for="text">Text to Analyze</label>
            <textarea id="text" name="text" rows="10" required></textarea>
        </div>
        
        <div class="form-actions">
            <button type="submit" class="button primary">Analyze</button>
        </div>
    </form>
    
    {% if message %}
    <div class="result-message">
        <p>{{ message }}</p>
    </div>
    {% endif %}
    
    {% if result %}
    <div class="result-box">
        <h2>Analysis Results</h2>
        
        <div class="score-display">
            <div class="score-bar">
                <div class="score-fill human" style="width: {{ result.human_score }}%">
                    <span>Human: {{ result.human_score }}%</span>
                </div>
                <div class="score-fill ai" style="width: {{ result.ai_score }}%">
                    <span>AI: {{ result.ai_score }}%</span>
                </div>
            </div>
        </div>
        
        <div class="analysis-details">
            <h3>Detailed Analysis</h3>
            <ul>
                <li>Formal Language: {{ result.analysis.formal_language }}%</li>
                <li>Repetitive Patterns: {{ result.analysis.repetitive_patterns }}%</li>
                <li>Sentence Uniformity: {{ result.analysis.sentence_uniformity }}%</li>
            </ul>
        </div>
    </div>
    {% endif %}
    {% endif %}
</section>
{% endblock %}
"""

# Account page
account_template = """
{% extends "base.html" %}

{% block content %}
<section class="account-page">
    <h1>Account Information</h1>
    
    <div class="account-info">
        <div class="info-card">
            <h2>User Information</h2>
            <p><strong>Username:</strong> {{ user.username }}</p>
            <p><strong>Plan:</strong> {{ plan.description }}</p>
            <p><strong>Words Remaining:</strong> {{ user.words_remaining }}</p>
            <p><strong>Joined Date:</strong> {{ user.created_at }}</p>
            <p><strong>Payment Status:</strong> <span class="status {{ 'success' if user.payment_status == 'Paid' else 'warning' }}">{{ user.payment_status }}</span></p>
        </div>
    </div>
    
    <div class="account-actions">
        <a href="{{ url_for('upgrade') }}" class="button">Upgrade Plan</a>
        <a href="{{ url_for('payment') }}" class="button">Make Payment</a>
    </div>
    
    <h2>Payment History</h2>
    
    {% if transactions %}
    <div class="table-container">
        <table class="data-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Subscription</th>
                    <th>Amount</th>
                    <th>Status</th>
                    <th>Reference</th>
                </tr>
            </thead>
            <tbody>
                {% for t in transactions %}
                <tr>
                    <td>{{ t.date }}</td>
                    <td>{{ t.subscription_type }}</td>
                    <td>${{ t.amount }}</td>
                    <td><span class="status {{ 'success' if t.status == 'Completed' else 'warning' }}">{{ t.status }}</span></td>
                    <td>{{ t.reference }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% else %}
    <p>No payment history available.</p>
    {% endif %}
</section>
{% endblock %}
"""

# Payment page
payment_template = """
{% extends "base.html" %}

{% block content %}
<section class="payment-page">
    <h1>Make a Payment</h1>
    
    <div class="plan-details">
        <h2>Your Plan: {{ plan.description }}</h2>
        <p>Amount Due: ${{ plan.price }}</p>
    </div>
    
    <form method="post" action="{{ url_for('payment') }}">
        <div class="form-group">
            <label for="phone_number">Phone Number for Payment</label>
            <input type="tel" id="phone_number" name="phone_number" pattern="[0-9]{10}" placeholder="0712345678" required>
            <small>Enter the phone number you want to use for M-Pesa payment</small>
        </div>
        
        <div class="form-actions">
            <button type="submit" class="button primary">Pay ${{ plan.price }}</button>
            <a href="{{ url_for('dashboard') }}" class="button">Cancel</a>
        </div>
    </form>
</section>
{% endblock %}
"""

# Upgrade plan page
upgrade_template = """
{% extends "base.html" %}

{% block content %}
<section class="upgrade-page">
    <h1>Upgrade Your Plan</h1>
    
    <div class="current-plan">
        <h2>Current Plan</h2>
        <div class="plan-card current">
            <h3>{{ current_plan.name }}</h3>
            <div class="price">${{ current_plan.price }}</div>
            <p>{{ current_plan.word_limit }} words per round</p>
            <p>{{ current_plan.description }}</p>
        </div>
    </div>
    
    <h2>Available Plans</h2>
    
    <div class="plan-selection">
        <form method="post" action="{{ url_for('upgrade') }}">
            <div class="plan-options">
                {% for name, plan in available_plans.items() %}
                <div class="plan-option">
                    <input type="radio" id="plan_{{ name }}" name="new_plan" value="{{ name }}" required>
                    <label for="plan_{{ name }}">
                        <div class="plan-card">
                            <h3>{{ name }}</h3>
                            <div class="price">${{ plan.price }}</div>
                            <p>{{ plan.word_limit }} words per round</p>
                            <p>{{ plan.description }}</p>
                        </div>
                    </label>
                </div>
                {% endfor %}
            </div>
            
            <div class="form-actions">
                <button type="submit" class="button primary">Upgrade</button>
                <a href="{{ url_for('dashboard') }}" class="button">Cancel</a>
            </div>
        </form>
    </div>
</section>
{% endblock %}
"""

# All templates in a dictionary
html_templates = {
    'base.html': base_layout,
    'index.html': index_template,
    'login.html': login_template,
    'register.html': register_template,
    'dashboard.html': dashboard_template,
    'humanize.html': humanize_template,
    'detect.html': detect_template,
    'account.html': account_template,
    'payment.html': payment_template,
    'upgrade.html': upgrade_template
}
