from app import create_app, db
from app.models.user import User
from app.models.role import Role
from app.models.menu import MenuItem, Ingredient
from app.models.recipe import Recipe
from app.models.inventory import InventoryItem, InventoryTransaction
from app.models.order import Order, OrderItem, DailySales
from werkzeug.security import generate_password_hash

app = create_app()

def init_roles():
    # Admin Role
    admin_role = Role(
        name='admin',
        description='Administrator with full access',
        permissions={'permissions': ['all']}
    )

    # Manager Role
    manager_role = Role(
        name='manager',
        description='Restaurant Manager',
        permissions={
            'permissions': [
                'view_staff',
                'manage_staff',
                'view_menu',
                'manage_menu',
                'view_inventory',
                'manage_inventory',
                'view_orders',
                'manage_orders',
                'view_reports',
                'view_audit_logs'  
            ]
        }
    )

    # Staff Role
    staff_role = Role(
        name='staff',
        description='Regular Staff Member',
        permissions={
            'permissions': [
                'view_menu',
                'view_inventory',
                'view_orders',
                'manage_orders'
            ]
        }
    )

    return [admin_role, manager_role, staff_role]

with app.app_context():
    # Drop all tables
    db.drop_all()
    
    # Create all tables
    db.create_all()
    
    # Initialize roles
    roles = init_roles()
    for role in roles:
        db.session.add(role)
    
    # Create a default admin user
    admin_user = User(
        name='Admin',
        email='admin@restaurant.com',
        password_hash=generate_password_hash('admin123'),
        restaurant_name='Test Restaurant',
        is_active=True
    )
    
    db.session.add(admin_user)
    db.session.commit()
    
    # Assign admin role to admin user
    admin_user.role = Role.query.filter_by(name='admin').first()
    db.session.commit()
    
    print("Database initialized successfully!")
