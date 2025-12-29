import os

from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="templates/assets")

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.secret_key = os.getenv('SECRET_KEY')

    db.init_app(app)
    bcrypt = Bcrypt(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    from blueprintapp.blueprints.auth.models import User
    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(int(uid))
    
    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect(url_for("auth.login"))

    from blueprintapp.blueprints.core.routes import core
    from blueprintapp.blueprints.auth.routes import auth
    from blueprintapp.blueprints.reviews.routes import reviews
    from blueprintapp.blueprints.admin.routes import admin

    app.register_blueprint(core, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(reviews, url_prefix="/reviews")
    app.register_blueprint(admin, url_prefix="/admin")

    migrate = Migrate(app, db)

    return app