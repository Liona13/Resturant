from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, EmailField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from app.models.user import User
from app.models.role import Role

class StaffForm(FlaskForm):
    """Form for creating and editing staff members"""
    email = EmailField('Email', validators=[
        DataRequired(),
        Email(),
        Length(min=6, max=120)
    ])
    name = StringField('Name', validators=[
        DataRequired(),
        Length(min=2, max=80)
    ])
    password = PasswordField('Password', validators=[
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        EqualTo('password', message='Passwords must match')
    ])
    role = SelectField('Role', coerce=int, validators=[DataRequired()])
    permissions = SelectMultipleField('Additional Permissions', choices=[
        ('manage_orders', 'Manage Orders'),
        ('view_inventory', 'View Inventory'),
        ('manage_inventory', 'Manage Inventory'),
        ('view_reports', 'View Reports')
    ])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Create Staff Account')

    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)
        # Populate role choices
        self.role.choices = [(role.id, role.name.title()) 
                           for role in Role.query.order_by(Role.name).all()]
        self.original_email = kwargs.get('original_email')

    def validate_email(self, field):
        """Validate email is unique"""
        user = User.query.filter_by(email=field.data).first()
        if self.original_email:
            if field.data != self.original_email:
                if user:
                    raise ValidationError('Email already registered.')
        else:
            if user:
                raise ValidationError('Email already registered.')
