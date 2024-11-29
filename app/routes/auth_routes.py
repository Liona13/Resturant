from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.login_attempt import LoginAttempt
from app.forms.auth_forms import LoginForm, RegistrationForm, ChangePasswordForm
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """User login route with security measures"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        ip_address = request.remote_addr
        user_agent = request.user_agent.string

        # Check if login is blocked
        if LoginAttempt.is_blocked(email, ip_address):
            remaining_minutes = LoginAttempt.get_block_duration(email, ip_address)
            flash(f'Too many failed attempts. Please try again in {remaining_minutes} minutes.', 'error')
            return render_template('auth/login.html', form=form)

        user = User.query.filter_by(email=email).first()
        
        # Record the login attempt
        attempt = LoginAttempt(
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            restaurant_name=user.restaurant_name if user else 'unknown',
            successful=False
        )
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account is deactivated. Please contact your administrator.', 'error')
                db.session.add(attempt)
                db.session.commit()
                return render_template('auth/login.html', form=form)
            
            # Successful login
            attempt.successful = True
            db.session.add(attempt)
            
            # Update user's last login
            user.last_login = datetime.utcnow()
            
            # Log the successful login
            AuditLog.log_action(
                user=user,
                action='login',
                details={
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'restaurant': user.restaurant_name
                },
                ip_address=ip_address
            )
            
            # Remember me functionality
            remember = form.remember_me.data
            login_user(user, remember=remember)
            
            db.session.commit()
            
            # Clean up old login attempts periodically
            LoginAttempt.cleanup_old_attempts()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.index')
            return redirect(next_page)
        else:
            # Failed login attempt
            db.session.add(attempt)
            db.session.commit()
            
            # Log failed login attempt
            AuditLog.log_action(
                user=user if user else None,
                action='failed_login',
                details={
                    'email': email,
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'restaurant': user.restaurant_name if user else 'unknown'
                },
                ip_address=ip_address
            )
            
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html', form=form)

@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            # Here you would typically send an email with the reset link
            # For now, we'll just flash the token (in production, never do this!)
            flash(f'Password reset link: {url_for("auth.reset_password", token=token, _external=True)}', 'info')
            
            # Create audit log entry
            AuditLog.create_log(
                user_id=user.id,
                action='password_reset_request',
                details=f'Password reset requested from IP: {request.remote_addr}'
            )
        else:
            # Don't reveal if email exists or not
            flash('If an account exists with that email, a password reset link will be sent.', 'info')
    
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Find user by token
    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.verify_reset_token(token):
        flash('Invalid or expired reset token', 'error')
        return redirect(url_for('auth.reset_password_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.clear_reset_token()
        
        # Create audit log entry
        AuditLog.create_log(
            user_id=user.id,
            action='password_reset',
            details=f'Password reset completed from IP: {request.remote_addr}'
        )
        
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password.html', title='Reset Password', form=form)

@auth.route('/logout')
@login_required
def logout():
    """Log out the current user"""
    try:
        # Log the logout action before actually logging out
        AuditLog.log_action(
            user=current_user,
            action='logout',
            details={
                'user_email': current_user.email,
                'timestamp': datetime.utcnow().isoformat()
            },
            ip_address=request.remote_addr,
            target_type='user',
            target_id=current_user.id
        )
        
        # Get user info before logout for flash message
        user_email = current_user.email
        
        # Perform the logout
        logout_user()
        
        flash(f'User {user_email} logged out successfully', 'success')
        return redirect(url_for('auth.login'))
    except Exception as e:
        flash(f'Error during logout: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Get the manager role for new restaurant registrations
        manager_role = Role.query.filter_by(name='manager').first()
        if not manager_role:
            flash('Error: System role not found. Please contact administrator.', 'error')
            return redirect(url_for('main.index'))

        user = User(
            email=form.email.data,
            name=form.name.data,
            restaurant_name=form.restaurant_name.data,
            role_id=manager_role.id
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! You can now log in as a Restaurant Manager.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Error during registration. Please try again.', 'error')
            return render_template('auth/register.html', title='Register', form=form)
            
    return render_template('auth/register.html', title='Register', form=form)

@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect', 'error')
            return render_template('auth/change_password.html', form=form)
        
        try:
            current_user.set_password(form.new_password.data)
            flash('Your password has been updated successfully', 'success')
            
            # Log the password change
            AuditLog.log_action(
                user=current_user,
                action='password_change',
                details={'ip_address': request.remote_addr},
                ip_address=request.remote_addr
            )
            
            return redirect(url_for('main.index'))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('auth/change_password.html', form=form)
    
    return render_template('auth/change_password.html', form=form)

# Apply password expiry check to all routes except auth routes
@auth.before_app_request
def check_password_expiry():
    if current_user.is_authenticated and not request.blueprint == 'auth':
        if current_user.password_expired():
            flash('Your password has expired. Please change it to continue.', 'warning')
            return redirect(url_for('auth.change_password'))
        
        days_left = current_user.days_until_password_expiry()
        if 0 < days_left <= 7:  # Warning period of 7 days
            flash(f'Your password will expire in {days_left} days. Please change it soon.', 'info')
