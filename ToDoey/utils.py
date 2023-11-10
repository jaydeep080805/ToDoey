from werkzeug.security import generate_password_hash, check_password_hash
from .models import UserInformation


def hash_password(password):
    return generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)


def verify_password(hashed_password, password_from_form):
    return check_password_hash(hashed_password, password_from_form)


def validate_email(form_email):
    return (
        False
        if UserInformation.query.filter_by(email=form_email).first()
        else form_email
    )
