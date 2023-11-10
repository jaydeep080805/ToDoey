from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from .forms import TaskForm, SignUpForm, LoginForm
from .models import UserInformation, TaskDataBase
from . import db, csrf
from flask_login import login_user, current_user, login_required
from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required,
)
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash


main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
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
        return redirect(url_for("main.home"))

    other_tasks = []
    due_today_tasks = []
    if current_user.is_authenticated:
        # get all the tasks associated with that user
        tasks = current_user.tasks

        # filter the tasks by due date
        other_tasks = [
            task
            for task in tasks
            if task.due_date != date.today() and task.completed != True
        ]
        due_today_tasks = [
            task
            for task in tasks
            if task.due_date == date.today() and task.completed != True
        ]

    for task in other_tasks:
        print(task.completed)

    return render_template(
        "index.html", form=form, task_list=other_tasks, due_today_tasks=due_today_tasks
    )


@main.route("/update_task", methods=["POST"])
@csrf.exempt
def update_task():
    # get the data from the ajax post
    data = request.get_json()
    if data:
        # get the task id
        task_id = data.get("task_id")
        # print(data["task_id"])

        task_to_update = TaskDataBase.query.get(task_id)
        try:
            task_to_update.completed = True
            db.session.commit()
            return jsonify({"status": "success"}), 200
        except:
            print("task not found")
            return jsonify({"status": "Error"})

    else:
        flash("An error has occured", "error")
        return (jsonify({"status": "error", "message": "No data received"}),)


@main.route("/about")
def about():
    return render_template("about.html")


@main.route("/profile")
def profile():
    user_info = UserInformation.query.filter_by(email=current_user.email).first()
    return render_template("profile.html", user_info=user_info)


@main.route("/sign-up", methods=["GET", "POST"])
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
                return redirect(url_for("home.sign_up"))
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

        return redirect(url_for("main.home"))

    return render_template("sign_up.html", form=form)


@main.route("/login", methods=["GET", "POST"])
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
                return redirect(url_for("main.home"))
        except:
            flash("Incorrect Login Data", "error")
            return redirect(url_for("main.login"))

    return render_template("login.html", form=form)


@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.home"))
