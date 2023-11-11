from werkzeug.security import generate_password_hash, check_password_hash
from .models import UserInformation
from flask_mail import Message
from . import mail
from threading import Thread
from flask import current_app


# generates a hashed password
def hash_password(password):
    return generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)


# checks a hashed password
def verify_password(hashed_password, password_from_form):
    return check_password_hash(hashed_password, password_from_form)


# checks if an email is valid,
# if it is then return the email,
# else return False
def validate_email(form_email):
    return (
        False
        if UserInformation.query.filter_by(email=form_email).first()
        else form_email
    )


# get a users account by their email
def get_user_by_email(email):
    return UserInformation.query.filter_by(email=email).first()


# get a users account by their id
def get_user_by_id(id):
    return UserInformation.query.get(id)


def send_async_email(app, msg):
    # Flask-Mail needs to run within an application context,
    with app.app_context():
        try:
            # Attempt to send the email.
            mail.send(msg)
        except Exception as e:
            # Log any exceptions that occur during the mail sending process.
            current_app.logger.error(f"An error occurred while sending an email: {e}")


# function to send an email
# takes the recipient and what information the user changed (name, email etc)
def updated_info_message(recipient, change):
    # Create a new message object with the subject, recipient, and body of the email.
    msg = Message(
        subject=f"{change} Change",
        recipients=[recipient],
        body=f"Your {change} has successfully been changed",
    )

    # Retrieve the current Flask app instance.
    # This is necessary because the new thread will not have access to the
    # Flask app context by default.
    app = current_app._get_current_object()

    # Start a new thread to send the email.
    # This allows the application to continue running and respond to web requests
    # without waiting for the email to be sent.
    Thread(target=send_async_email, args=(app, msg)).start()
