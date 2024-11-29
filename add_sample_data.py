from app import create_app, db
from app.models.menu import MenuItem, Ingredient
from app.models.recipe import Recipe
from app.models.inventory import InventoryItem, InventoryTransaction
from app.models.user import User
from datetime import datetime

app = create_app()

def add_sample_data():
    with app.app_context():
        try:
            # Get admin user
            admin_user = User.query.filter_by(email='admin@example.com').first()
            if not admin_user:
                print("Error: Admin user not found. Please run create_test_users.py first.")
                return

            # Add sample ingredients
            ingredients = [
                Ingredient(
                    name='Rice', 
                    cost_per_unit=2.50, 
                    unit='kg', 
                    user_id=admin_user.id
                ),
                Ingredient(
                    name='Chicken', 
                    cost_per_unit=8.00, 
                    unit='kg', 
                    user_id=admin_user.id
                ),
                Ingredient(
                    name='Tomatoes', 
                    cost_per_unit=3.50, 
                    unit='kg', 
                    user_id=admin_user.id
                ),
                Ingredient(
                    name='Onions', 
                    cost_per_unit=1.50, 
                    unit='kg', 
                    user_id=admin_user.id
                ),
                Ingredient(
                    name='Garlic', 
                    cost_per_unit=5.00, 
                    unit='kg', 
                    user_id=admin_user.id
                ),
                Ingredient(
                    name='Olive Oil', 
                    cost_per_unit=12.00, 
                    unit='l', 
                    user_id=admin_user.id
                ),
                Ingredient(
                    name='Pasta', 
                    cost_per_unit=2.00, 
                    unit='kg', 
                    user_id=admin_user.id
                ),
                Ingredient(
                    name='Cheese', 
                    cost_per_unit=15.00, 
                    unit='kg', 
                    user_id=admin_user.id
                ),
                Ingredient(
                    name='Bread', 
                    cost_per_unit=3.00, 
                    unit='kg', 
                    user_id=admin_user.id
                ),
                Ingredient(
                    name='Butter', 
                    cost_per_unit=10.00, 
                    unit='kg', 
                    user_id=admin_user.id
                ),
                Ingredient(
                    name='Tea Leaves', 
                    cost_per_unit=20.00, 
                    unit='kg', 
                    user_id=admin_user.id
                ),
                Ingredient(
                    name='Chocolate', 
                    cost_per_unit=12.00, 
                    unit='kg', 
                    user_id=admin_user.id
                ),
                Ingredient(
                    name='Flour', 
                    cost_per_unit=1.50, 
                    unit='kg', 
                    user_id=admin_user.id
                ),
                Ingredient(
                    name='Sugar', 
                    cost_per_unit=2.00, 
                    unit='kg', 
                    user_id=admin_user.id
                ),
                Ingredient(
                    name='Milk', 
                    cost_per_unit=2.50, 
                    unit='l', 
                    user_id=admin_user.id
                )
            ]
            
            for ingredient in ingredients:
                existing = Ingredient.query.filter_by(
                    name=ingredient.name,
                    user_id=admin_user.id
                ).first()
                if not existing:
                    db.session.add(ingredient)
            
            db.session.commit()  # Commit to get ingredient IDs

            # Get ingredients by name for recipe creation
            ingredient_dict = {i.name: i for i in Ingredient.query.filter_by(user_id=admin_user.id).all()}

            # Add sample menu items with recipes
            menu_items = [
                {
                    'item': {
                        'name': 'Chicken Biryani',
                        'description': 'Fragrant rice dish with tender chicken and aromatic spices',
                        'price': 15.99,
                        'cost': 5.50,
                        'category': 'main_course',
                        'user_id': admin_user.id
                    },
                    'recipe': [
                        ('Rice', 0.3, 'kg'),
                        ('Chicken', 0.4, 'kg'),
                        ('Onions', 0.2, 'kg'),
                        ('Garlic', 0.05, 'kg'),
                    ]
                },
                {
                    'item': {
                        'name': 'Pasta Carbonara',
                        'description': 'Classic Italian pasta with creamy sauce and cheese',
                        'price': 12.99,
                        'cost': 4.00,
                        'category': 'main_course',
                        'user_id': admin_user.id
                    },
                    'recipe': [
                        ('Pasta', 0.2, 'kg'),
                        ('Cheese', 0.1, 'kg'),
                        ('Butter', 0.05, 'kg'),
                    ]
                },
                {
                    'item': {
                        'name': 'Chocolate Cake',
                        'description': 'Rich and moist chocolate cake',
                        'price': 8.99,
                        'cost': 3.00,
                        'category': 'dessert',
                        'user_id': admin_user.id
                    },
                    'recipe': [
                        ('Flour', 0.2, 'kg'),
                        ('Sugar', 0.2, 'kg'),
                        ('Chocolate', 0.15, 'kg'),
                        ('Butter', 0.1, 'kg'),
                        ('Milk', 0.2, 'l'),
                    ]
                }
            ]

            for menu_data in menu_items:
                existing_item = MenuItem.query.filter_by(
                    name=menu_data['item']['name'],
                    user_id=admin_user.id
                ).first()
                
                if not existing_item:
                    menu_item = MenuItem(**menu_data['item'])
                    db.session.add(menu_item)
                    db.session.commit()  # Commit to get menu_item.id

                    # Create recipe entries
                    for ingredient_name, quantity, unit in menu_data['recipe']:
                        ingredient = ingredient_dict.get(ingredient_name)
                        if ingredient:
                            recipe = Recipe(
                                menu_item_id=menu_item.id,
                                ingredient_id=ingredient.id,
                                quantity=quantity,
                                unit=unit
                            )
                            db.session.add(recipe)
                    db.session.commit()

            # Add initial inventory for each ingredient
            for ingredient in Ingredient.query.filter_by(user_id=admin_user.id).all():
                existing_inventory = InventoryItem.query.filter_by(
                    ingredient_id=ingredient.id,
                    user_id=admin_user.id
                ).first()
                
                if not existing_inventory:
                    inventory_item = InventoryItem(
                        ingredient_id=ingredient.id,
                        quantity=10.0,  # Initial stock
                        minimum_stock=5.0,  # Reorder point
                        last_restock_date=datetime.utcnow(),
                        user_id=admin_user.id
                    )
                    db.session.add(inventory_item)
                    db.session.commit()  # Commit to get inventory_item.id

                    # Add initial stock transaction
                    transaction = InventoryTransaction(
                        inventory_item_id=inventory_item.id,
                        transaction_type='restock',
                        quantity=10.0,
                        transaction_date=datetime.utcnow(),
                        user_id=admin_user.id,
                        unit_cost=ingredient.cost_per_unit,
                        notes='Initial stock'
                    )
                    db.session.add(transaction)
                    db.session.commit()

            print("Sample data added successfully!")
            
        except Exception as e:
            print(f"Error adding sample data: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    add_sample_data()
