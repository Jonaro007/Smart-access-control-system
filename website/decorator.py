from functools import wraps
from flask import redirect, url_for, flash, session
from flask_login import current_user

def verify_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        
        if not session.get("auth", False):
            flash("Please confirm your two-factor authentication first", "error")
            return redirect(url_for('verify.google_auth'))  # Prüfe Endpoint!
        
        return f(*args, **kwargs)
    return decorated_function
