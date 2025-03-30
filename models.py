# This file provides in-memory session storage for demonstration purposes
# In a production environment, you would use a database or other persistent storage

# In-memory user database (only used for session storage, not persistent)
users_db = {}

# In-memory transactions database (only used for session storage, not persistent)
transactions_db = []

# Helper functions
def get_user_data(username):
    """Get a user from the session storage"""
    return users_db.get(username)

def user_exists(username):
    """Check if a user exists in the session storage"""
    return username in users_db

def create_user_session(username, user_data):
    """Create or update a user session"""
    users_db[username] = user_data

def get_transaction(transaction_id):
    """Get a transaction from the session storage"""
    for transaction in transactions_db:
        if transaction.get('transaction_id') == transaction_id:
            return transaction
    return None

def add_transaction(transaction_data):
    """Add a transaction to the session storage"""
    transactions_db.append(transaction_data)

def update_transaction(transaction_id, status, reference=None):
    """Update a transaction in the session storage"""
    for transaction in transactions_db:
        if transaction.get('transaction_id') == transaction_id:
            transaction['status'] = status
            if reference:
                transaction['reference'] = reference
            return True
    return False

def clear_session():
    """Clear all session data"""
    users_db.clear()
    transactions_db.clear()
