from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
login.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    from app.models.user import User
    from app.models.role import Role
    
    from app.routes.main_routes import main
    from app.routes.auth_routes import auth
    from app.routes.menu_routes import menu
    from app.routes.inventory_routes import inventory
    from app.routes.order_routes import orders
    from app.routes.recipe_routes import recipe
    from app.routes.profile_routes import profile
    from app.routes.admin_routes import admin
    from app.routes.staff_routes import staff
    
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(menu, url_prefix='/menu')
    app.register_blueprint(inventory, url_prefix='/inventory')
    app.register_blueprint(orders, url_prefix='/orders')
    app.register_blueprint(recipe, url_prefix='/recipe')
    app.register_blueprint(profile, url_prefix='/profile')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(staff, url_prefix='/staff')

    # Create admin role if it doesn't exist
    with app.app_context():
        db.create_all()
        from app.models.role import Role
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', description='Administrator')
            db.session.add(admin_role)
            db.session.commit()

    return app
