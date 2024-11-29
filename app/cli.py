"""CLI commands for the application."""
import click
from flask.cli import with_appcontext
from app import db
from app.models.role import Role
from app.models.user import User

@click.command('init-roles')
@with_appcontext
def init_roles_command():
    """Initialize roles with proper permissions."""
    # Define roles and their permissions
    roles = {
        'admin': {
            'description': 'Administrator with full access',
            'permissions': ['all']
        },
        'manager': {
            'description': 'Restaurant manager',
            'permissions': [
                'manage_menu',
                'view_menu',
                'manage_inventory',
                'view_inventory',
                'manage_orders',
                'view_orders',
                'manage_staff',
                'view_staff',
                'view_reports'
            ]
        },
        'staff': {
            'description': 'Regular staff member',
            'permissions': [
                'view_menu',
                'view_inventory',
                'manage_orders',
                'view_orders'
            ]
        }
    }

    # Create or update roles
    for role_name, role_data in roles.items():
        role = Role.query.filter_by(name=role_name).first()
        if role is None:
            role = Role(name=role_name)
        
        role.description = role_data['description']
        role.permissions = {'permissions': role_data['permissions']}
        db.session.add(role)

    try:
        db.session.commit()
        print("Successfully initialized roles with permissions.")
    except Exception as e:
        db.session.rollback()
        print(f"Error initializing roles: {str(e)}")

@click.command('create-admin')
@click.argument('email')
@click.argument('password')
@with_appcontext
def create_admin_command(email, password):
    """Create an admin user."""
    # Get admin role
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        print("Error: Admin role not found. Please run init-roles first.")
        return

    # Check if user exists
    user = User.query.filter_by(email=email).first()
    if user:
        # Update existing user to admin
        user.role = admin_role
        print(f"Updated existing user {email} to admin role.")
    else:
        # Create new admin user
        user = User(
            email=email,
            name='Admin',
            role=admin_role
        )
        user.set_password(password)
        db.session.add(user)
    
    try:
        db.session.commit()
        print(f"Successfully {'updated' if user else 'created'} admin user with email: {email}")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating admin user: {str(e)}")
