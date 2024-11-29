from app import db
from datetime import datetime

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    profit_margin = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add relationship to Recipe and User
    recipe_items = db.relationship('Recipe', back_populates='menu_item', cascade='all, delete-orphan')
    user = db.relationship('User', backref=db.backref('menu_items', lazy=True))

    def __init__(self, **kwargs):
        super(MenuItem, self).__init__(**kwargs)
        self.profit_margin = self.calculate_profit_margin()

    def calculate_profit_margin(self):
        """Calculate profit margin as a percentage"""
        if self.cost == 0:
            return 100.0
        return ((self.price - self.cost) / self.price) * 100

    def update_cost_from_recipe(self):
        """Update the item's cost based on its recipe ingredients"""
        total_cost = sum(recipe.calculate_cost() for recipe in self.recipe_items)
        self.cost = total_cost
        self.profit_margin = self.calculate_profit_margin()
        return total_cost

    def update_price(self, new_price):
        """Update the item price and recalculate profit margin"""
        self.price = new_price
        self.profit_margin = self.calculate_profit_margin()
        self.updated_at = datetime.utcnow()

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    cost_per_unit = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)  # e.g., 'kg', 'g', 'l', 'ml', 'piece'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add relationship to Recipe and User
    recipe_items = db.relationship('Recipe', back_populates='ingredient', cascade='all, delete-orphan')
    inventory_item = db.relationship('InventoryItem', uselist=False, back_populates='ingredient')
    user = db.relationship('User', backref=db.backref('ingredients', lazy=True))
