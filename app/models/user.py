from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login
from flask import current_app

class PasswordHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256))
    restaurant_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    _is_active = db.Column('is_active', db.Boolean, nullable=False, default=True)
    last_login = db.Column(db.DateTime)
    password_changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    password_history = db.relationship('PasswordHistory', backref='user', lazy='dynamic')
    login_count = db.Column(db.Integer, server_default=db.text('0'), nullable=False)
    failed_login_count = db.Column(db.Integer, server_default=db.text('0'), nullable=False)
    last_failed_login = db.Column(db.DateTime, nullable=True)
    reset_token = db.Column(db.String(100))
    reset_token_expiry = db.Column(db.DateTime)
    __table_args__ = (
        db.UniqueConstraint('reset_token', name='uix_user_reset_token'),
    )
    role = db.relationship('Role', back_populates='users', lazy=True)

    def set_password(self, password):
        """Set password with history tracking"""
        # Skip history check for new users (no existing password)
        if self.password_hash and self.check_password_history(password):
            raise ValueError('Password was used recently. Choose a different password.')
        
        # Add current password to history before changing
        if self.password_hash and self.id:  # Only add to history if user exists in db
            history = PasswordHistory(user_id=self.id, password_hash=self.password_hash)
            db.session.add(history)
            
            # Remove old password history entries
            old_passwords = self.password_history.order_by(PasswordHistory.created_at.desc())\
                .offset(current_app.config['PASSWORD_HISTORY_SIZE']).all()
            for old_pwd in old_passwords:
                db.session.delete(old_pwd)
        
        self.password_hash = generate_password_hash(password)
        self.password_changed_at = datetime.utcnow()
        
        if self.id:  # Only commit if user exists in db
            db.session.commit()

    def check_password(self, password):
        """Check if password is correct"""
        return check_password_hash(self.password_hash, password)

    def check_password_history(self, new_password):
        """Check if password was used recently"""
        for history in self.password_history.order_by(PasswordHistory.created_at.desc())\
                .limit(current_app.config['PASSWORD_HISTORY_SIZE']).all():
            if check_password_hash(history.password_hash, new_password):
                return True
        return False

    def password_expired(self):
        """Check if password has expired"""
        if not self.password_changed_at:
            return True
        expiry_date = self.password_changed_at + timedelta(days=current_app.config['PASSWORD_EXPIRY_DAYS'])
        return datetime.utcnow() > expiry_date

    def days_until_password_expiry(self):
        """Get number of days until password expires"""
        if not self.password_changed_at:
            return 0
        expiry_date = self.password_changed_at + timedelta(days=current_app.config['PASSWORD_EXPIRY_DAYS'])
        days = (expiry_date - datetime.utcnow()).days
        return max(0, days)

    def has_permission(self, permission):
        """Check if user has a specific permission through their role"""
        if not self.role:
            return False
        return self.role.has_permission(permission)

    def is_admin(self):
        """Check if user has admin role"""
        return self.role.name == 'admin'

    def get_active_status(self):
        """Get the active status of the user"""
        return self._is_active

    def set_active_status(self, value):
        """Set the active status of the user"""
        self._is_active = value

    # Override UserMixin's is_active property
    is_active = property(get_active_status, set_active_status)

    def record_login(self, success=True):
        """Record login attempt"""
        if success:
            self.last_login = datetime.utcnow()
            # Refresh the session to get current counter values
            db.session.refresh(self)
            self.login_count = (self.login_count or 0) + 1
            self.failed_login_count = 0  # Reset failed attempts on successful login
        else:
            self.last_failed_login = datetime.utcnow()
            # Refresh the session to get current counter values
            db.session.refresh(self)
            self.failed_login_count = (self.failed_login_count or 0) + 1
        db.session.add(self)
        db.session.commit()

    def generate_reset_token(self):
        """Generate password reset token"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=24)
        db.session.commit()
        return self.reset_token

    def verify_reset_token(self, token):
        """Verify if reset token is valid"""
        if (self.reset_token != token or 
            not self.reset_token_expiry or 
            self.reset_token_expiry < datetime.utcnow()):
            return False
        return True

    def clear_reset_token(self):
        """Clear reset token after use"""
        self.reset_token = None
        self.reset_token_expiry = None
        db.session.commit()

    def __repr__(self):
        return f'<User {self.email}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
