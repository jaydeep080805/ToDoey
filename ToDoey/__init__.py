from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import environ, path
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import logging
from logging.handlers import RotatingFileHandler

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()

UPLOAD_FOLDER = path.join("ToDoey", "static", "images")


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = environ["SECRET_KEY"]
    app.config["SQLALCHEMY_DATABASE_URI"] = environ["DATABASE_URL"]
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # Logging configuration
    if not app.debug:
        handler = RotatingFileHandler("app.log", maxBytes=10000, backupCount=1)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        handler.setLevel(logging.DEBUG)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)

    with app.app_context():
        db.create_all()

    from .views import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from .models import UserInformation

    @login_manager.user_loader
    def load_user(user_id):
        return UserInformation.query.get(int(user_id))

    return app
