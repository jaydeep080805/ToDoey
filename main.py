from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from forms import TaskForm, SignUpForm, LoginForm
from os import environ
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from flask_login import (
    current_user,
    LoginManager,
    login_user,
    logout_user,
    UserMixin,
    login_required,
)
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from datetime import date, datetime

load_dotenv()

app = Flask(__name__)
db = SQLAlchemy()
login_manager = LoginManager(app)

# app config
app.secret_key = environ["SECRET_KEY"]
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
db.init_app(app)
csrf = CSRFProtect(app)
migrate = Migrate(app, db)


class TaskDataBase(db.Model):
    # TODO add a description option so you can make a popout menu to edit the task
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("user_information.id"), nullable=False)
    task = db.Column(db.String(), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    category = db.Column(db.String())
    user = db.relationship("UserInformation", back_populates="tasks")


class UserInformation(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    profile_pic = db.Column(db.String(), nullable=True)
    creation_date = db.Column(db.Date, default=date.today())
    tasks = db.relationship(
        "TaskDataBase", order_by=TaskDataBase.due_date, back_populates="user"
    )


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return UserInformation.query.get(int(user_id))


@app.route("/", methods=["GET", "POST"])
def home():
    form = TaskForm()

    if request.method == "POST":
        # for testing only
        print(form.task.data)
        print(form.due_date.data)
        # print(form.category.data)

        due_date_provided = form.due_date.data
        if due_date_provided == None:
            today = datetime.today()
            # print(type(today))
            due_date_provided = today

        new_task = TaskDataBase(
            user_id=current_user.id,
            task=form.task.data,
            due_date=due_date_provided,
            category=form.category.data,
        )
        db.session.add(new_task)
        db.session.commit()

        flash("Task Added Successfully", "success")
        return redirect(url_for("home"))

    other_tasks = []
    due_today_tasks = []
    if current_user.is_authenticated:
        # get all the tasks associated with that user
        tasks = current_user.tasks

        # filter the tasks by due date
        other_tasks = [task for task in tasks if task.due_date != date.today()]
        due_today_tasks = [task for task in tasks if task.due_date == date.today()]

    return render_template(
        "index.html", form=form, task_list=other_tasks, due_today_tasks=due_today_tasks
    )


@app.route("/update_task", methods=["POST"])
@csrf.exempt
def update_task():
    # get the data from the ajax post
    data = request.get_json()
    if data:
        # get the task id
        task_id = data.get("task_id")
        # print(data["task_id"])

        task_to_delete = TaskDataBase.query.get(task_id)
        try:
            db.session.delete(task_to_delete)
            db.session.commit()
            return jsonify({"status": "success"}), 200
        except:
            print("task not found")
            return jsonify({"status": "Error"})

    else:
        flash("An error has occured", "error")
        return (jsonify({"status": "error", "message": "No data received"}),)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/profile")
def profile():
    user_info = UserInformation.query.filter_by(email=current_user.email).first()
    return render_template("profile.html", user_info=user_info)


@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    form = SignUpForm()

    if form.validate_on_submit():
        # grab the information from the form
        name_to_add = form.name.data
        email_to_add = form.email.data
        password_to_add = generate_password_hash(
            form.password.data, method="pbkdf2:sha256", salt_length=16
        )

        # query the database to see if the email already exists in there
        email_from_database = UserInformation.query.filter_by(
            email=email_to_add
        ).first()

        try:
            # if the email does exist then send a flash saying it exists
            if email_from_database.email == email_to_add:
                flash("Email Already Exists!", "error")
                return redirect(url_for("sign_up"))
        except:
            print("Email is valid")

        # make a new object and add it to the database
        user_login_details = UserInformation(
            name=name_to_add, email=email_to_add, password=password_to_add
        )

        db.session.add(user_login_details)
        db.session.commit()

        email_from_database = UserInformation.query.filter_by(
            email=email_to_add
        ).first()

        flash("Successfully Created Account!", "success")
        login_user(email_from_database)

        return redirect(url_for("home"))

    return render_template("sign_up.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        # get the data from the form
        email_from_form = form.email.data
        password_from_form = form.password.data

        # query the database to see if the email already exists in there
        email_from_database = UserInformation.query.filter_by(
            email=email_from_form
        ).first()

        try:
            check_password = check_password_hash(
                email_from_database.password, password_from_form
            )
            # check if all the details are correct
            if email_from_form == email_from_database.email and check_password == True:
                flash("Successfully Logged In", "success")
                login_user(email_from_database)
                return redirect(url_for("home"))
        except:
            flash("Incorrect Login Data", "error")
            return redirect(url_for("login"))

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
