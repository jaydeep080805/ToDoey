from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import environ
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = environ["SECRET_KEY"]
    app.config["SQLALCHEMY_DATABASE_URI"] = environ["DATABASE_URL"]

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()

    from .views import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from .models import UserInformation

    @login_manager.user_loader
    def load_user(user_id):
        return UserInformation.query.get(int(user_id))

    return app
