from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    DateField,
    SubmitField,
    EmailField,
    PasswordField,
    SelectField,
    FileField,
    RadioField,
    BooleanField,
)
from wtforms.validators import DataRequired, Regexp
from flask_ckeditor import CKEditorField


# Form for creating a new task
class TaskForm(FlaskForm):
    task = StringField("Task", validators=[DataRequired()])
    due_date = DateField("Due date")
    category = SelectField("Category", choices=["Personal", "Work"])
    submit = SubmitField("Submit")


# Form for user sign-up
class SignUpForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Form for user login
class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Form for changing user's name
class ChangeNameForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Form for changing user's email
class ChangeEmailForm(FlaskForm):
    current_email = EmailField("Current Email", validators=[DataRequired()])
    new_email = EmailField("New Email", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Form for changing user's password
class ChangePasswordForm(FlaskForm):
    current_password = StringField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Form for changing user's profile picture
class ChangeProfilePic(FlaskForm):
    profile_pic = FileField("Profile picture")
    submit = SubmitField("Submit")


class NotificationsForm(FlaskForm):
    want_notifications = RadioField(
        "Notifications", choices=[("yes", "Yes"), ("no", "No")]
    )
    notification_email = BooleanField("Email")
    notification_text = BooleanField("Text")
    submit = SubmitField("Save Changes")


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    subject = StringField("Subject", validators=[DataRequired()])
    message = CKEditorField("Message", validators=[DataRequired()])
    submit = SubmitField("Submit")


class AddNumberForm(FlaskForm):
    number = StringField(
        "New Number",
        validators=[
            DataRequired(),
            Regexp(
                # UK phone numbers, excluding country code, are usually 10 or 11 digits.
                r"^0\d{10,11}$",
                message="Phone number must be a valid UK number without country code.",
            ),
        ],
    )
    submit = SubmitField("Submit")


class ChangeNumberForm(FlaskForm):
    current_number = StringField(
        "Current Number",
        validators=[
            DataRequired(),
            Regexp(
                r"^0\d{10,11}$",
                message="Phone number must be a valid UK number without country code.",
            ),
        ],
    )
    new_number = StringField("New Number", validators=[DataRequired()])
    submit = SubmitField("Submit")
