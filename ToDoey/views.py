# imports
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    jsonify,
    current_app,
)
from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required,
    AnonymousUserMixin,
)
from datetime import date, datetime

# custom imports
from .forms import TaskForm, SignUpForm, LoginForm, ChangeNameForm, ChangeEmailForm
from .models import UserInformation, TaskDataBase
from . import db, csrf
from .utils import (
    hash_password,
    verify_password,
    validate_email,
    get_user_by_email,
    get_user_by_id,
)


main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
def home():
    form = TaskForm()

    try:
        if request.method == "POST":
            # for testing only
            current_app.logger.debug(form.task.data)
            current_app.logger.debug(form.due_date.data)
            current_app.logger.debug(form.category.data)

            due_date_provided = form.due_date.data
            if due_date_provided == None:
                today = datetime.today()
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
    except AttributeError as e:
        current_app.logger.error(f"Create Task error (user not logged in): {e}")
        flash("Must have an account to create task", "error")
        return redirect(url_for("main.sign_up"))

    except Exception as e:
        current_app.logger.error(f"Create Task error (Unknown): {e}")

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

    return render_template(
        "index.html", form=form, task_list=other_tasks, due_today_tasks=due_today_tasks
    )


@main.route("/update_task", methods=["POST"])
def update_task():
    # get the data from the ajax post
    data = request.get_json()
    if data:
        # get the task id
        task_id = data.get("task_id")

        task_to_update = TaskDataBase.query.get(task_id)
        try:
            task_to_update.completed = True
            db.session.commit()
            return jsonify({"status": "success"}), 200
        except Exception as e:
            current_app.logger.error(f"Task update error (Unknown): {e}")
            current_app.logger.error("Task not found for ID: " + str(task_id))
            return jsonify({"status": "Error"})

    else:
        flash("An error has occured", "error")
        return (jsonify({"status": "error", "message": "No data received"}),)


@main.route("/about")
def about():
    return render_template("about.html")


@main.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    form = SignUpForm()

    if form.validate_on_submit():
        # grab the information from the form
        name_to_add = form.name.data
        email_to_add = validate_email(form.email.data)
        password_to_add = hash_password(form.password.data)

        # if the email does exist then send a flash saying it exists
        try:
            if not email_to_add:
                flash("Email Already Exists!", "error")
                return render_template("sign_up.html", form=form)
        except AttributeError:
            current_app.logger.info(
                "if this prints then the email did not match one in the database and the users email is valid"
            )
        except Exception as e:
            current_app.logger.error(f"Signup error (Unknown): {e}")

        # make a new object and add it to the database
        user_login_details = UserInformation(
            name=name_to_add.title(), email=email_to_add, password=password_to_add
        )

        try:
            db.session.add(user_login_details)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Database error (Unknown): {e}")

        flash("Successfully Created Account!", "success")
        login_user(user_login_details)

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
            check_password = verify_password(
                email_from_database.password, password_from_form
            )
            # check if all the details are correct
            if email_from_database and check_password == True:
                flash("Successfully Logged In", "success")
                login_user(email_from_database)
                return redirect(url_for("main.home"))
            else:
                flash("Incorrect Password", "error")

        except AttributeError:
            flash("That email doesn't exist", "error")

        except Exception as e:
            current_app.logger.error(f"Login error (Unknown): {e}")

    return render_template("login.html", form=form)


@main.route("/profile")
@login_required
def profile():
    user_info = get_user_by_email(current_user.email)
    return render_template("profile.html", user_info=user_info)


@main.route("/change_name", methods=["GET", "POST"])
@login_required
def change_name():
    form = ChangeNameForm()

    if form.validate_on_submit():
        # gets the current users account by their id (my own function)
        user_to_change = get_user_by_id(current_user.id)
        # change their name
        user_to_change.name = form.name.data
        # then commit the changes and alert the user
        db.session.commit()
        flash("Successfully changed name", "success")
        return redirect(url_for("main.profile"))

    return render_template("change_name.html", form=form)


@main.route("/change_email", methods=["GET", "POST"])
@login_required
def change_email():
    form = ChangeEmailForm()

    if form.validate_on_submit():
        # if the current email entered is correct
        # this will check if the emails are the same
        # and you cannot use the same email more than once
        if form.current_email.data == current_user.email:
            new_email = form.new_email.data
            # if the new email is not currently in the db (is valid)
            if validate_email(new_email):
                current_user.email = validate_email(new_email)

                db.session.commit()
                flash("Successfully changed email", "success")
                return redirect(url_for("main.profile"))

            # if the email is already in the db (not valid/used by someone else)
            else:
                flash("That email is already in use", "error")

    return render_template("change_email.html", form=form)


@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.home"))
