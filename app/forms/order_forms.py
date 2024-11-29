from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField, FloatField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange
from app.models.order import OrderStatus, PaymentMethod

class OrderForm(FlaskForm):
    table_number = IntegerField('Table Number', validators=[Optional()])
    server_name = StringField('Server Name', validators=[DataRequired()])
    status = SelectField('Status', 
                        choices=[(status.value, status.value.replace('_', ' ').title()) 
                                for status in OrderStatus],
                        validators=[Optional()],
                        default=OrderStatus.PENDING.value)
    payment_method = SelectField('Payment Method',
                               choices=[(method.value, method.value.replace('_', ' ').title()) 
                                      for method in PaymentMethod],
                               validators=[Optional()])
    tax_amount = FloatField('Tax Amount', validators=[NumberRange(min=0)], default=0.0)
    tip_amount = FloatField('Tip Amount', validators=[NumberRange(min=0)], default=0.0)
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Submit Order')

class OrderItemForm(FlaskForm):
    menu_item_id = SelectField('Menu Item', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)], default=1)
    special_instructions = TextAreaField('Special Instructions', validators=[Optional()])
    submit = SubmitField('Add to Order')

    def __init__(self, *args, **kwargs):
        super(OrderItemForm, self).__init__(*args, **kwargs)
        from app.models.menu import MenuItem
        # Populate menu items dropdown
        menu_items = MenuItem.query.all()
        self.menu_item_id.choices = [(item.id, f"{item.name} - ${item.price:.2f}") 
                                   for item in menu_items]
