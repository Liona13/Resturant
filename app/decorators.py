from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user
from app.models.audit_log import AuditLog

def permission_required(permission):
    """
    Decorator that checks if the current user has the required permission.
    Usage: @permission_required('manage_menu')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('main.login'))
            
            if not current_user.has_permission(permission):
                # Log unauthorized access attempt
                AuditLog.log_action(
                    user=current_user,
                    action='unauthorized_access',
                    details={
                        'required_permission': permission,
                        'attempted_endpoint': request.endpoint,
                        'attempted_url': request.url,
                    },
                    ip_address=request.remote_addr,
                    target_type='permission',
                    target_id=None
                )
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """
    Decorator that checks if the current user is an admin.
    Usage: @admin_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('main.login'))
        
        if not current_user.is_admin():
            flash('This page is restricted to administrators.', 'error')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    """
    Decorator that checks if the current user is a manager or admin.
    Usage: @manager_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('main.login'))
        
        if not (current_user.is_admin() or current_user.role.name == 'manager'):
            # Log unauthorized manager access attempt
            AuditLog.log_action(
                user=current_user,
                action='unauthorized_manager_access',
                details={
                    'attempted_endpoint': request.endpoint,
                    'attempted_url': request.url,
                },
                ip_address=request.remote_addr,
                target_type='role',
                target_id=None
            )
            flash('This page is restricted to managers and administrators.', 'error')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function
