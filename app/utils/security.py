from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def check_password_expiry(view_func):
    """Decorator to check if user's password has expired"""
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if current_user.is_authenticated and not current_user.is_anonymous:
            # Skip password expiry check for password change route
            if view_func.__name__ == 'change_password':
                return view_func(*args, **kwargs)
            
            # Check if password has expired
            if current_user.password_expired():
                flash('Your password has expired. Please change it to continue.', 'warning')
                return redirect(url_for('auth.change_password'))
            
            # Warn user if password is about to expire
            days_left = current_user.days_until_password_expiry()
            if 0 < days_left <= 7:  # Warning period of 7 days
                flash(f'Your password will expire in {days_left} days. Please change it soon.', 'info')
        
        return view_func(*args, **kwargs)
    return wrapped_view

def validate_password_strength(password):
    """Validate password against complexity requirements"""
    errors = []
    
    # Check minimum length
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    # Check for uppercase letters
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    # Check for lowercase letters
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    # Check for digits
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one number")
    
    # Check for special characters
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        errors.append("Password must contain at least one special character")
    
    return errors
