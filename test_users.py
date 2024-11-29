from app import create_app, db
from app.models.user import User
from app.models.role import Role
from werkzeug.security import generate_password_hash

app = create_app()

def create_test_users():
    with app.app_context():
        # Create test users for each role
        test_users = [
            {
                'email': 'manager@restaurant.com',
                'password': 'manager123',
                'name': 'Test Manager',
                'restaurant_name': 'Test Restaurant',
                'role_name': 'manager'
            },
            {
                'email': 'staff@restaurant.com',
                'password': 'staff123',
                'name': 'Test Staff',
                'restaurant_name': 'Test Restaurant',
                'role_name': 'staff'
            }
        ]

        for user_data in test_users:
            # Check if user already exists
            user = User.query.filter_by(email=user_data['email']).first()
            if not user:
                # Get role
                role = Role.query.filter_by(name=user_data['role_name']).first()
                if not role:
                    print(f"Role {user_data['role_name']} not found!")
                    continue

                # Create user
                user = User(
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    name=user_data['name'],
                    restaurant_name=user_data['restaurant_name'],
                    role_id=role.id
                )
                db.session.add(user)
                print(f"\nCreated {role.name} user:")
                print(f"Email: {user.email}")
                print(f"Password: {user_data['password']}")

        try:
            db.session.commit()
            print("\nAll test users created successfully!")
            
            print("\nAvailable test accounts:")
            print("\n1. Admin Account:")
            print("Email: admin@restaurant.com")
            print("Password: admin123")
            
            print("\n2. Manager Account:")
            print("Email: manager@restaurant.com")
            print("Password: manager123")
            
            print("\n3. Staff Account:")
            print("Email: staff@restaurant.com")
            print("Password: staff123")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating test users: {str(e)}")

if __name__ == '__main__':
    create_test_users()
