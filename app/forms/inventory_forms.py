from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class InventoryItemForm(FlaskForm):
    minimum_stock = FloatField('Minimum Stock Level', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save')

class InventoryTransactionForm(FlaskForm):
    transaction_type = SelectField('Transaction Type', 
                                 choices=[('restock', 'Restock'), ('usage', 'Usage')],
                                 validators=[DataRequired()])
    quantity = FloatField('Quantity', validators=[DataRequired(), NumberRange(min=0.01)])
    unit_cost = FloatField('Unit Cost', validators=[NumberRange(min=0)])
    notes = TextAreaField('Notes')
    submit = SubmitField('Submit Transaction')

class RecipeScalingForm(FlaskForm):
    servings = FloatField('Number of Servings', validators=[DataRequired(), NumberRange(min=0.1)])
    submit = SubmitField('Scale Recipe')
