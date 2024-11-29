from app import create_app, db
from app.models import User, Role
from werkzeug.security import generate_password_hash

app = create_app()

def update_users():
    with app.app_context():
        # Get the admin and manager roles
        admin_role = Role.query.filter_by(name='admin').first()
        manager_role = Role.query.filter_by(name='manager').first()
        
        if not admin_role or not manager_role:
            print("Error: Required roles not found!")
            return

        # Create admin user if no users exist
        if User.query.count() == 0:
            admin_user = User(
                email='admin@restaurant.com',
                password_hash=generate_password_hash('admin123'),
                name='System Admin',
                restaurant_name='Main Restaurant',
                role_id=admin_role.id,
                is_active=True
            )
            db.session.add(admin_user)
            print("\nCreated admin user:")
            print(f"Email: admin@restaurant.com")
            print(f"Password: admin123")

        # Update all users without a role
        users = User.query.filter_by(role_id=None).all()
        for user in users:
            user.role_id = manager_role.id
            if not user.name:
                user.name = user.email.split('@')[0]  # Use email username as name
        
        db.session.commit()

        print("\nUsers in database:")
        for user in User.query.all():
            print(f"- {user.email} (Role: {user.role.name if user.role else 'None'}, Name: {user.name})")

if __name__ == '__main__':
    update_users()
