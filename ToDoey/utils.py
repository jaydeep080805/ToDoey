from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from threading import Thread
from flask import current_app
from sqlalchemy.orm import load_only
from os import environ

from .models import UserInformation
from . import mail


# Define a function to handle threading
def run_in_thread(target_function, *args):
    thread = Thread(target=target_function, args=args)
    thread.start()

    if thread:
        return True
    else:
        return False


# Get the current Flask app context
def get_current_app_context():
    return current_app._get_current_object()


# Generate a hashed password
def generate_hashed_password(password):
    # Generate a hashed password using PBKDF2 with SHA-256 and a salt length of 16.
    return generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)


# Verify a hashed password
def verify_password(hashed_password, password_from_form):
    # Check if the provided password matches the hashed password.
    return check_password_hash(hashed_password, password_from_form)


# Check if an email is valid, if it is, return the email; otherwise, return False
def is_email_valid(form_email):
    # Check if the email is unique in the database.
    exists = (
        UserInformation.query.filter_by(email=form_email)
        .options(load_only(UserInformation.id))
        .first()
    )
    return False if exists else form_email


# Get a user's account by their email from the database
def get_user_by_email_from_db(email):
    # Retrieve a user's account by their email from the database.
    return (
        UserInformation.query.filter_by(email=email)
        .options(load_only(UserInformation.id))
        .first()
    )


# Get a user's account by their ID from the database
def get_user_by_id_from_db(id):
    # Retrieve a user's account by their ID from the database.
    return UserInformation.query.get(id)


# Send a confirmation email to the recipient
def send_email_confirmation(recipient):
    app = get_current_app_context()
    with app.app_context():
        try:
            msg = Message(
                subject="Email Received",
                recipients=[recipient],
                body="We have received your email and will respond shortly.",
            )
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(e)


def send_asyc_email(app, msg):
    # Flask-Mail needs to run within an application context,
    with app.app_context():
        try:
            # Attempt to send the email.
            mail.send(msg)

        except Exception as e:
            # Log any exceptions that occur during the mail sending process.
            current_app.logger.error(f"An error occurred while sending an email: {e}")


# Send an email to notify about updated information (e.g., name, email)
def send_updated_info_email(recipient, change):
    msg = Message(
        subject=f"{change} Change",
        recipients=[recipient],
        body=f"Your {change} has been successfully changed",
    )

    app = get_current_app_context()
    run_in_thread(send_asyc_email, app, msg, recipient)


def contact_email(name, email, subject, message):
    # Create a new message object with the subject, recipient, and body of the email.
    msg = Message(
        subject=subject,
        recipients=[environ.get("EMAIL")],
        body=f"{message} \n\nSent from {name}:{email}",
    )

    app = get_current_app_context()
    email_thread = run_in_thread(send_asyc_email, app, msg)

    if email_thread:
        return True

    else:
        return False


# checks which notifications the user has on and sends the messages accordingly
def check_notification_type(recipient, change):
    try:
        if recipient.wants_notifications:
            # index 0 is for email
            # index 1 is for text
            notification_type = recipient.notification_type.split(",")

            # get the value for each notification type
            # IMPORTANT: switch the values to bools
            # as they will always evaluate to true
            # since they're strings
            email_notification = True if notification_type[0] == "True" else False
            text_notification = True if notification_type[1] == "True" else False

            if email_notification and text_notification:
                send_updated_info_email(recipient.email, change)

            elif email_notification:
                print("email")
                send_updated_info_email(recipient.email, change)

            elif text_notification:
                print("text")

    except Exception as e:
        current_app.logger.error(e)
