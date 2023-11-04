from flask_wtf import FlaskForm
from wtforms import StringField, DateField ,SubmitField, EmailField, PasswordField, SelectField
from wtforms.validators import DataRequired

class TaskForm(FlaskForm):
    task = StringField("Task", validators=[DataRequired()])
    due_date = DateField("Due date")
    category = SelectField("Catgegory", choices=["Personal", "Work"])
    submit = SubmitField("Submit")

class SignUpForm(FlaskForm):
    email = EmailField("Email", [DataRequired()])
    password = PasswordField("Password", [DataRequired()])
    submit = SubmitField("Submit")