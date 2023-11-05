from flask import Flask, render_template, redirect, url_for, request, flash
from forms import TaskForm, SignUpForm, LoginForm
from os import environ
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, LoginManager, login_user, logout_user, UserMixin
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
db = SQLAlchemy()
login_manager = LoginManager(app)

# app config
app.secret_key = environ["SECRET_KEY"]
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
db.init_app(app)
csrf = CSRFProtect(app)


class TaskDataBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(), nullable=False)
    due_date = db.Column(db.Date, nullable=True)


class UserInformation(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)


with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return UserInformation.query.get(int(user_id))


@app.route("/", methods=["GET", "POST"])
def home():
    form = TaskForm()
    return render_template("index.html", form=form, task_list=[])


@app.route("/about")
def about():
    return


@app.route("/profile")
def profile():
    return


@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    form = SignUpForm()

    if form.validate_on_submit():
        # grab the information from the form
        email_to_add = form.email.data
        password_to_add = generate_password_hash(
            form.password.data, method="pbkdf2:sha256", salt_length=16
        )

        # query the database to see if the email already exists in there
        check_email = UserInformation.query.filter_by(email=email_to_add).first()

        try:
            # if the email does exist then send a flash saying it exists
            if check_email.email == email_to_add:
                flash("Email Already Exists!", "error")
                return redirect(url_for("sign_up"))
        except:
            print("Email is valid")

        # make a new object and add it to the database
        user_login_details = UserInformation(
            email=email_to_add, password=password_to_add
        )

        db.session.add(user_login_details)
        db.session.commit()

        flash("Successfully Created Account!", "success")
        return redirect(url_for("sign_up"))

    return render_template("sign_up.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        # get the data from the form
        email_from_form = form.email.data
        password_from_form = form.password.data

        # query the database to see if the email already exists in there
        email_from_database = UserInformation.query.filter_by(email=email_from_form).first()
        check_password = check_password_hash(email_from_database.password, password_from_form)

        # check if all the details are correct
        if email_from_form == email_from_database.email and check_password == True:
            flash("Successfully Logged In", "success")
            login_user(email_from_database)
            return redirect(url_for("home"))
        

    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
