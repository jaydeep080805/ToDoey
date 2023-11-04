from flask import Flask, render_template
from forms import TaskForm, SignUpForm
from os import environ
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, LoginManager

app = Flask(__name__)
db = SQLAlchemy()
login_manager = LoginManager(app)

# app config
app.secret_key = environ["SECRET_KEY"]
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
db.init_app(app)


class TaskDataBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(), nullable=False)
    due_date = db.Column(db.Date, nullable=True)


class SignUp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)


with app.app_context():
    db.create_all()


@login_manager.user_loader
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
    return render_template("sign_up.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    return


if __name__ == "__main__":
    app.run(debug=True)
