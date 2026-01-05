from flask import Flask
from config import Config
from app.extensions import db, login_manager, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view = 'auth.login'

    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Register Blueprints
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.admin import bp as admin_bp
    from app.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Template Filter
    @app.template_filter('ribuan')
    def format_ribuan(value):
        if value is None:
            return "0"
        return "{:,.0f}".format(value).replace(',', '.')

    return app
