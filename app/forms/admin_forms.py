from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired

class UserRoleForm(FlaskForm):
    """Form for editing a user's role"""
    role = SelectField('Role', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Update Role')
