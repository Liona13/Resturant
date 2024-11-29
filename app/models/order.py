from datetime import datetime
from app import db
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PaymentMethod(Enum):
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    MOBILE_PAYMENT = "mobile_payment"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING)
    table_number = db.Column(db.Integer)
    server_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    payment_method = db.Column(db.Enum(PaymentMethod))
    total_amount = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    tip_amount = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    user = db.relationship('User', backref=db.backref('orders', lazy=True))

    def calculate_total(self):
        """Calculate total amount including items, tax, and tip"""
        subtotal = sum(item.subtotal for item in self.items)
        self.total_amount = subtotal + self.tax_amount + self.tip_amount
        return self.total_amount

    def update_inventory(self):
        """Update inventory levels based on ordered items"""
        for order_item in self.items:
            menu_item = order_item.menu_item
            if menu_item and menu_item.recipe_items:
                for recipe_item in menu_item.recipe_items:
                    if recipe_item.ingredient and recipe_item.ingredient.inventory_item:
                        # Calculate quantity needed based on recipe and order quantity
                        quantity_needed = recipe_item.quantity * order_item.quantity
                        inventory_item = recipe_item.ingredient.inventory_item
                        inventory_item.quantity -= quantity_needed
                        if inventory_item.quantity < inventory_item.minimum_stock:
                            # TODO: Implement low stock notification
                            pass

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    special_instructions = db.Column(db.Text)
    
    # Relationship
    menu_item = db.relationship('MenuItem')
    
    @property
    def subtotal(self):
        """Calculate subtotal for this item"""
        return self.quantity * self.unit_price

class DailySales(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    total_sales = db.Column(db.Float, default=0.0)
    total_orders = db.Column(db.Integer, default=0)
    average_order_value = db.Column(db.Float, default=0.0)
    total_tax = db.Column(db.Float, default=0.0)
    total_tips = db.Column(db.Float, default=0.0)

    # Relationship
    user = db.relationship('User', backref=db.backref('daily_sales', lazy=True))

    def update_from_orders(self, orders):
        """Update daily sales statistics from a list of orders"""
        if not orders:
            return

        self.total_sales = sum(order.total_amount for order in orders)
        self.total_orders = len(orders)
        self.average_order_value = self.total_sales / self.total_orders if self.total_orders > 0 else 0
        self.total_tax = sum(order.tax_amount for order in orders)
        self.total_tips = sum(order.tip_amount for order in orders)
