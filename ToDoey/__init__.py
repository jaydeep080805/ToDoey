from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import environ, path
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import logging
from logging.handlers import RotatingFileHandler
from flask_mail import Mail

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()
mail = Mail()

UPLOAD_FOLDER = path.join("ToDoey", "static", "images")


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = environ.get("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = environ.get("DATABASE_URL")
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_USERNAME"] = environ.get("EMAIL")
    app.config["MAIL_PASSWORD"] = environ.get("EMAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = environ.get("EMAIL")

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

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
