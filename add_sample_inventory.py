from app import create_app, db
from app.models.menu import Ingredient
from app.models.inventory import InventoryItem, InventoryTransaction
from datetime import datetime, timedelta

app = create_app()

def add_sample_inventory():
    with app.app_context():
        # Get all ingredients
        ingredients = Ingredient.query.all()
        
        # Add inventory items for each ingredient
        for ingredient in ingredients:
            inventory = InventoryItem(
                ingredient_id=ingredient.id,
                quantity=10.0,  # Start with 10 units of each
                minimum_stock=5.0  # Set minimum stock to 5 units
            )
            db.session.add(inventory)
            
            # Add some sample transactions
            transactions = [
                # Initial stock
                InventoryTransaction(
                    inventory_item=inventory,
                    transaction_type='restock',
                    quantity=10.0,
                    unit_cost=ingredient.cost_per_unit,
                    transaction_date=datetime.utcnow() - timedelta(days=7),
                    notes='Initial stock'
                ),
                # Usage
                InventoryTransaction(
                    inventory_item=inventory,
                    transaction_type='usage',
                    quantity=2.0,
                    transaction_date=datetime.utcnow() - timedelta(days=5),
                    notes='Regular usage'
                ),
                # Restock
                InventoryTransaction(
                    inventory_item=inventory,
                    transaction_type='restock',
                    quantity=5.0,
                    unit_cost=ingredient.cost_per_unit * 1.1,  # 10% price increase
                    transaction_date=datetime.utcnow() - timedelta(days=2),
                    notes='Regular restock'
                ),
                # More usage
                InventoryTransaction(
                    inventory_item=inventory,
                    transaction_type='usage',
                    quantity=3.0,
                    transaction_date=datetime.utcnow() - timedelta(days=1),
                    notes='Regular usage'
                )
            ]
            
            for transaction in transactions:
                db.session.add(transaction)
        
        try:
            db.session.commit()
            print("Sample inventory data added successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding sample inventory data: {str(e)}")

if __name__ == '__main__':
    add_sample_inventory()
