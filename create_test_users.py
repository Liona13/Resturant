from app import create_app, db
from app.models import User, Role
from werkzeug.security import generate_password_hash

app = create_app()

def create_test_users():
    with app.app_context():
        # Test users data
        test_users = [
            {
                'email': 'admin@example.com',
                'password': 'Admin123!',
                'name': 'Admin User',
                'role_name': 'admin',
                'phone': '555-0100',
                'restaurant_name': 'Test Restaurant'
            },
            {
                'email': 'manager@example.com',
                'password': 'Manager123!',
                'name': 'Manager User',
                'role_name': 'manager',
                'phone': '555-0200',
                'restaurant_name': 'Test Restaurant'
            },
            {
                'email': 'staff1@example.com',
                'password': 'Staff123!',
                'name': 'Staff One',
                'role_name': 'staff',
                'phone': '555-0301',
                'restaurant_name': 'Test Restaurant'
            },
            {
                'email': 'staff2@example.com',
                'password': 'Staff123!',
                'name': 'Staff Two',
                'role_name': 'staff',
                'phone': '555-0302',
                'restaurant_name': 'Test Restaurant'
            }
        ]

        # Create users
        for user_data in test_users:
            # Check if user already exists
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if existing_user:
                print(f"User {user_data['email']} already exists")
                continue

            # Get role
            role = Role.query.filter_by(name=user_data['role_name']).first()
            if not role:
                print(f"Role {user_data['role_name']} not found")
                continue

            # Create new user
            new_user = User(
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password']),
                name=user_data['name'],
                role=role,
                phone=user_data['phone'],
                restaurant_name=user_data['restaurant_name']
            )
            db.session.add(new_user)
            print(f"Created user: {user_data['email']} with role: {user_data['role_name']}")

        try:
            db.session.commit()
            print("\nAll test users created successfully!")
            print("\nTest Users Credentials:")
            for user in test_users:
                print(f"\n{user['role_name'].title()}:")
                print(f"Email: {user['email']}")
                print(f"Password: {user['password']}")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating users: {str(e)}")

if __name__ == '__main__':
    create_test_users()
