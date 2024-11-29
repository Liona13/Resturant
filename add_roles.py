from app import create_app, db
from app.models import Role

app = create_app()

def add_default_roles():
    with app.app_context():
        # Create default roles if they don't exist
        roles = [
            {
                'name': 'admin',
                'description': 'Administrator with full access',
                'permissions': {'permissions': ['all']}
            },
            {
                'name': 'manager',
                'description': 'Restaurant manager',
                'permissions': {
                    'permissions': [
                        'manage_menu',
                        'manage_inventory',
                        'manage_orders',
                        'view_reports',
                        'manage_staff'
                    ]
                }
            },
            {
                'name': 'staff',
                'description': 'Restaurant staff',
                'permissions': {
                    'permissions': [
                        'manage_orders',
                        'view_inventory'
                    ]
                }
            }
        ]

        # First delete existing roles
        Role.query.delete()
        db.session.commit()

        # Add new roles
        for role_data in roles:
            role = Role(**role_data)
            db.session.add(role)
        
        db.session.commit()
        print("\nRoles in database:")
        for role in Role.query.all():
            print(f"- {role.name}: {role.permissions}")

if __name__ == '__main__':
    add_default_roles()
