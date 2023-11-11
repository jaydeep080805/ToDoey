from werkzeug.security import generate_password_hash, check_password_hash
from .models import UserInformation
from flask_mail import Message
import smtplib
from os import environ


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


# function to send an email
# takes the recipient and what information the user changed (name, email etc)
def updated_info_message(recipient, change):
    my_email = environ["EMAIL"]
    password = environ["EMAIL_PASSWORD"]

    # create a connection
    connection = smtplib.SMTP("smtp.gmail.com", port=587)

    # makes the connection secure with encryption
    connection.starttls()
    # login to our account
    connection.login(user=my_email, password=password)

    # send an email
    connection.sendmail(
        from_addr=my_email,
        to_addrs=recipient,
        msg=f"Subject:{change} Change\n\nYour {change} has successfully been changed",
    )
