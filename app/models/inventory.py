from app import db
from datetime import datetime

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=0)
    minimum_stock = db.Column(db.Float, nullable=False, default=0)
    last_restock_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    ingredient = db.relationship('Ingredient', back_populates='inventory_item')
    user = db.relationship('User', backref=db.backref('inventory_items', lazy=True))

    def needs_restock(self):
        """Check if the item needs restocking"""
        return self.quantity <= self.minimum_stock

class InventoryTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_item.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'restock' or 'usage'
    quantity = db.Column(db.Float, nullable=False)
    unit_cost = db.Column(db.Float)  # Cost per unit for restock transactions
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

    # Relationships
    inventory_item = db.relationship('InventoryItem', backref='transactions')
    user = db.relationship('User', backref=db.backref('inventory_transactions', lazy=True))
