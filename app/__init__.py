from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
login_manager.login_message = 'Please log in to access this page.'


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.main import main_bp
    app.register_blueprint(main_bp)

    from app.products import products_bp
    app.register_blueprint(products_bp, url_prefix='/products')

    from app.supply import supply_bp
    app.register_blueprint(supply_bp, url_prefix='/supply')

    from app.compliance import compliance_bp
    app.register_blueprint(compliance_bp, url_prefix='/compliance')

    from app.public import public_bp
    app.register_blueprint(public_bp, url_prefix='/public')

    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    with app.app_context():
        db.create_all()
        from app.models import Role
        Role.insert_roles()

    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('errors/404.html'), 404

    return app
