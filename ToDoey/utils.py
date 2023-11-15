from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from threading import Thread
from flask import current_app
from sqlalchemy.orm import load_only
from os import environ
from datetime import date, timedelta
from string import punctuation

from .models import UserInformation
from . import mail


# =========== utility functions for the other functions =========== #
# Get the current Flask app context
def get_current_app_context():
    return current_app._get_current_object()


# Define a function to handle threading
def run_in_thread(target_function, *args, **kwargs):
    thread = Thread(target=target_function, args=args, kwargs=kwargs)
    thread.start()

    if thread:
        return True
    else:
        return False


# =========== TASK FUNCTIONS =========== #
def get_filtered_tasks(tasks):
    # Calculate the start and end dates for the next 7 days (excluding today)
    today = date.today()
    start_of_week = today + timedelta(days=1)  # Start from tomorrow
    end_of_week = start_of_week + timedelta(days=6)

    due_today_tasks = [
        task for task in tasks if task.due_date == today and not task.completed
    ]

    due_this_week = [
        task
        for task in tasks
        if task.due_date != today
        and task.due_date >= start_of_week
        and task.due_date <= end_of_week
        and not task.completed
    ]

    task_list = [
        task for task in tasks if task.due_date > end_of_week and not task.completed
    ]

    return due_today_tasks, due_this_week, task_list


# =========== EMAIL FUNCTIONS =========== #
# Check if an email is valid, if it is, return the email; otherwise, return False
def is_email_valid(form_email):
    # Check if the email is unique in the database.
    exists = (
        UserInformation.query.filter_by(email=form_email)
        .options(load_only(UserInformation.id))
        .first()
    )
    return False if exists else form_email


# =========== PASSWORD FUNCTIONS =========== #
# Generate a hashed password
def generate_hashed_password(password):
    # Generate a hashed password using PBKDF2 with SHA-256 and a salt length of 16.
    return generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)


# Verify a hashed password
def verify_password(hashed_password, password_from_form):
    # Check if the provided password matches the hashed password.
    return check_password_hash(hashed_password, password_from_form)


def check_if_password_secure(password):
    # too short
    if len(password) < 8:
        return "Password is too short."

    # no uppercase chars
    elif not any(char.isupper() for char in password):
        return "Password should contain at least one uppercase letter."

    # no special chars
    elif not any(char in punctuation for char in password):
        return "Password should contain at least one special character"

    else:
        return True


# =========== DATABASE QUERY FUNCTIONS =========== #
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


# =========== NOTIFICATION FUNCTIONS =========== #
# send email to user about account changes
def send_asyc_email(subject, recipient, body, **kwargs):
    # Flask-Mail needs to run within an application context,
    if "app" in kwargs:
        app = kwargs["app"]

    else:
        app = get_current_app_context()

    with app.app_context():
        try:
            # confimation email for contact form
            if "name" in kwargs and "confirmation_message" in kwargs:
                msg = Message(
                    subject=f"{subject}",
                    recipients=[recipient],
                    body=f"{kwargs['confirmation_message']}",
                )
                mail.send(msg)
                return True

            # email sent to me from contact form
            elif "name" in kwargs:
                msg = Message(
                    subject=f"{subject}",
                    recipients=[environ.get("EMAIL")],
                    body=f"{body}\n\n{kwargs['name']}:{recipient}",
                )
                mail.send(msg)
                return True

            # changing info
            else:
                msg = Message(
                    subject=f"{subject}",
                    recipients=[recipient],
                    body=f"{body} has been changed successfully",
                )
                mail.send(msg)
                return True

        except Exception as e:
            # Log any exceptions that occur during the mail sending process.
            current_app.logger.error(f"An error occurred while sending an email: {e}")


# checks which notifications the user has on and sends the messages accordingly
def check_notification_type(recipient, subject, body):
    try:
        if recipient.wants_notifications:
            # index 0 is for email
            # index 1 is for text
            notification_type = recipient.notification_type.split(",")

            # get the value for each notification type
            # IMPORTANT: switch the values to bools
            # as they will always evaluate to true since they're strings
            email_notification = True if notification_type[0] == "True" else False
            text_notification = True if notification_type[1] == "True" else False

            app = get_current_app_context()

            if email_notification and text_notification:
                run_in_thread(send_asyc_email, subject, recipient.email, body, app=app)

            elif email_notification:
                run_in_thread(send_asyc_email, subject, recipient.email, body, app=app)

            elif text_notification:
                print("text")

    except Exception as e:
        current_app.logger.error(e)
