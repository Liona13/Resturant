from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    """Login form with security features"""
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(min=6, max=120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, max=128)
    ])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """Registration form with enhanced validation"""
    name = StringField('Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(min=6, max=120)
    ])
    restaurant_name = StringField('Restaurant Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, max=128, message='Password must be between 8 and 128 characters'),
        # Add password complexity requirements
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

    def validate_email(self, email):
        """Check if email is already registered"""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email address already registered.')

    def validate_password(self, password):
        """Enforce password complexity requirements"""
        pwd = password.data
        if not any(char.isupper() for char in pwd):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not any(char.islower() for char in pwd):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not any(char.isdigit() for char in pwd):
            raise ValidationError('Password must contain at least one number.')
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?' for char in pwd):
            raise ValidationError('Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)')

class ChangePasswordForm(FlaskForm):
    """Form for changing password"""
    current_password = PasswordField('Current Password', validators=[
        DataRequired(),
        Length(min=8, max=128)
    ])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, max=128)
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')

    def validate_new_password(self, field):
        """Validate password complexity"""
        from app.utils.security import validate_password_strength
        errors = validate_password_strength(field.data)
        if errors:
            raise ValidationError('\n'.join(errors))
