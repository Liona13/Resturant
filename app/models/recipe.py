from app import db
from datetime import datetime

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    menu_item = db.relationship('MenuItem', back_populates='recipe_items')
    ingredient = db.relationship('Ingredient', back_populates='recipe_items')

    def calculate_cost(self):
        """Calculate the cost of this recipe item based on ingredient cost and quantity"""
        if self.unit == self.ingredient.unit:
            return self.quantity * self.ingredient.cost_per_unit
        else:
            # Add conversion logic here if needed
            # For now, assume same unit is used
            return self.quantity * self.ingredient.cost_per_unit
