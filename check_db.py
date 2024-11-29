from app import create_app, db
from app.models import Role, User

app = create_app()

with app.app_context():
    print("\nRoles in database:\n")
    for role in Role.query.all():
        print(f"- {role.name}: {role.permissions}")
    
    print("\nUsers in database:\n")
    for user in User.query.all():
        print(f"- {user.email} (Role: {user.role.name if user.role else 'None'}, Name: {user.name})")
