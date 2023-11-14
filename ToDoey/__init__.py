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
from flask_ckeditor import CKEditor

# Load environment variables from a .env file
load_dotenv()

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()
mail = Mail()
ckeditor = CKEditor()

# Set upload folder path for profile pictures
UPLOAD_FOLDER = path.join("ToDoey", "static", "images")


# Function to create and configure the Flask app
def create_app():
    app = Flask(__name__)

    # Flask app configuration

    # Secret key for session management
    app.config["SECRET_KEY"] = environ.get("SECRET_KEY")

    # Database URL for SQLAlchemy
    app.config["SQLALCHEMY_DATABASE_URI"] = environ.get("DATABASE_URL")

    # Upload folder for profile pictures
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    # Flask mail configuration
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_USERNAME"] = environ.get("EMAIL")
    app.config["MAIL_PASSWORD"] = environ.get("EMAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = environ.get("EMAIL")

    # Initialize Flask extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    ckeditor.init_app(app)

    # Logging configuration
    if not app.debug:
        # Configure rotating log files for production
        handler = RotatingFileHandler("app.log", maxBytes=10000, backupCount=1)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        handler.setLevel(logging.DEBUG)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)

    # Create database tables within the app context
    with app.app_context():
        db.create_all()

    # Register blueprints
    from .views import main as main_blueprint

    app.register_blueprint(main_blueprint)

    # User loader for Flask-Login
    from .models import UserInformation

    @login_manager.user_loader
    def load_user(user_id):
        return UserInformation.query.get(int(user_id))

    return app
