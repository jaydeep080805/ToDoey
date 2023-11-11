from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    DateField,
    SubmitField,
    EmailField,
    PasswordField,
    SelectField,
    FileField,
)
from wtforms.validators import DataRequired


class TaskForm(FlaskForm):
    task = StringField("Task", validators=[DataRequired()])
    due_date = DateField("Due date")
    category = SelectField("Category", choices=["Personal", "Work"])
    submit = SubmitField("Submit")


class SignUpForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ChangeNameForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ChangeEmailForm(FlaskForm):
    current_email = EmailField("Current Email", validators=[DataRequired()])
    new_email = EmailField("New Email", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ChangePasswordForm(FlaskForm):
    current_password = StringField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ChangeProfilePic(FlaskForm):
    profile_pic = FileField("Profile picture")
    submit = SubmitField("Submit")
