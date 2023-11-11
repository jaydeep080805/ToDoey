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
)
from datetime import date, datetime
from werkzeug.utils import secure_filename
import uuid
from os import path, makedirs

# custom imports
from .forms import (
    TaskForm,
    SignUpForm,
    LoginForm,
    ChangeNameForm,
    ChangeEmailForm,
    ChangePasswordForm,
    ChangeProfilePic,
)
from .models import UserInformation, TaskDataBase
from . import db
from .utils import (
    hash_password,
    verify_password,
    validate_email,
    get_user_by_email,
    get_user_by_id,
    updated_info_message,
)


main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
def home():
    form = TaskForm()

    try:
        if request.method == "POST":
            # for testing only
            # current_app.logger.debug(form.task.data)
            # current_app.logger.debug(form.due_date.data)
            # current_app.logger.debug(form.category.data)

            # check if the user did not provide a date
            due_date_provided = form.due_date.data
            if due_date_provided == None:
                # set the due date for today
                today = datetime.today()
                due_date_provided = today

            # create an object to add to the Task db
            new_task = TaskDataBase(
                user_id=current_user.id,
                task=form.task.data,
                due_date=due_date_provided,
                category=form.category.data,
            )
            # add and commit the changes
            db.session.add(new_task)
            db.session.commit()

            flash("Task Added Successfully", "success")
            return redirect(url_for("main.home"))

    # this should execute if the user tries to make a task without being logged in
    except AttributeError as e:
        current_app.logger.error(f"Create Task error (user not logged in): {e}")
        flash("Must have an account to create task", "error")
        return redirect(url_for("main.sign_up"))

    # any other exceptions that can happen
    except Exception as e:
        current_app.logger.error(f"Create Task error (Unknown): {e}")

    other_tasks = []  # tasks that aren't due today
    due_today_tasks = []  # tasks that are due today
    if current_user.is_authenticated:
        # get all the tasks associated with that user
        tasks = current_user.tasks

        # filter the tasks by due date
        other_tasks = [
            task
            for task in tasks
            if task.due_date != date.today()
            and task.completed != True  # if the task isn't completed and NOT due today
        ]
        due_today_tasks = [
            task
            for task in tasks
            if task.due_date == date.today()
            and task.completed != True  # if the task isn't completed and IS due today
        ]

    return render_template(
        "index.html", form=form, task_list=other_tasks, due_today_tasks=due_today_tasks
    )


@main.route("/update_task", methods=["POST"])
def update_task():
    # get the data from the ajax post
    data = request.get_json()
    if data:
        # get the task id from the ajax req
        task_id = data.get("task_id")

        # gets the task from the database by the id
        task_to_update = TaskDataBase.query.get(task_id)
        try:
            task_to_update.completed = True
            db.session.commit()
            return jsonify({"status": "success"}), 200

        except Exception as e:
            current_app.logger.error(f"Task update error (Unknown): {e}")
            current_app.logger.error("Task not found for ID: " + str(task_id))
            return jsonify({"status": "Error"})

    # if data is None (no data passed through)
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
        email_to_add = validate_email(
            form.email.data
        )  # returns false if the email is invalid
        password_to_add = hash_password(form.password.data)

        # if the email does exist then send a flash saying it exists
        try:
            # if the email is invalid
            if not email_to_add:
                flash("Email Already Exists!", "error")
                return render_template("sign_up.html", form=form)

        # catch any exceptions
        except Exception as e:
            flash("Unknown error occured", "error")
            current_app.logger.error(f"Signup error (Unknown): {e}")

        # make a new object and add it to the database
        user_login_details = UserInformation(
            name=name_to_add.title(), email=email_to_add, password=password_to_add
        )

        # try block incase of any database errors
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

        # try block is only successful if the email_from_database evaluates to true
        # else it will throw an attribute error
        try:
            # checks if the passwords match
            check_password = verify_password(
                email_from_database.password, password_from_form
            )
            # check if the email and password are correct
            if email_from_database and check_password == True:
                flash("Successfully Logged In", "success")
                login_user(email_from_database)
                return redirect(url_for("main.home"))

            # this will only run if there is an incorrect password
            else:
                flash("Incorrect Password", "error")

        # if the email is incorrect
        except AttributeError:
            flash("That email doesn't exist", "error")

        # catch other exceptions
        except Exception as e:
            current_app.logger.error(f"Login error (Unknown): {e}")

    return render_template("login.html", form=form)


@main.route("/profile")
@login_required
def profile():
    # TODO let users choose if they want notifications

    # gets the current users account by their email (my own function, utils.py)
    user_info = get_user_by_email(current_user.email)

    # get the users profile picture
    image_file = url_for("static", filename=f"/images/{current_user.profile_pic}")
    return render_template("profile.html", user_info=user_info, image_file=image_file)


@main.route("/change_name", methods=["GET", "POST"])
@login_required
def change_name():
    form = ChangeNameForm()

    if form.validate_on_submit():
        # gets the current users account by their id (my own function, utils.py)
        user_to_change = get_user_by_id(current_user.id)

        # change their name
        user_to_change.name = form.name.data

        # then commit the changes and alert the user
        db.session.commit()
        flash("Successfully changed name", "success")

        # send an email about the change
        updated_info_message(current_user.email, "Username")
        return redirect(url_for("main.profile"))

    return render_template("change_name.html", form=form)


@main.route("/change_email", methods=["GET", "POST"])
@login_required
def change_email():
    form = ChangeEmailForm()

    if form.validate_on_submit():
        # if the entered email from the form is the same as the current users email
        if form.current_email.data == current_user.email:
            new_email = form.new_email.data

            # if the new email is not currently in the db (is ready to change)
            if validate_email(new_email):
                current_user.email = validate_email(new_email)

                db.session.commit()
                flash("Successfully changed email", "success")

                # send an email to the previous email to let them know their email has changed
                # TODO let the user report if it is unauthorised
                updated_info_message(form.current_email.data, "Email")

                return redirect(url_for("main.profile"))

            # if the email is already in the db (not valid/used by someone else)
            else:
                flash("That email is already in use", "error")

        # if the email doesnt match their current email
        else:
            flash("That is not the correct email", "error")

    return render_template("change_email.html", form=form)


@main.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        # get the "current_password" input from the form
        current_pass = form.current_password.data

        # if the current password matches the loged in users pass
        if verify_password(current_user.password, current_pass):
            new_pass = form.new_password.data
            confirm_pass = form.confirm_password.data

            # if the two passwords from the form are the same (the user confirmed their change)
            if new_pass == confirm_pass:
                # hash and salt the new password
                current_user.password = hash_password(form.new_password.data)

                # commit the changes and let the user know
                db.session.commit()
                flash("Password successfully changed", "success")

                # send an email about the change
                updated_info_message(current_user.email, "Password")
                return redirect(url_for("main.profile"))

            else:
                flash("Passwords do not match", "error")
        else:
            flash("Incorrect Password", "error")

    return render_template("change_password.html", form=form)


@main.route("/change_pic", methods=["GET", "POST"])
@login_required
def change_pic():
    form = ChangeProfilePic()
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

    if form.validate_on_submit():
        raw_profile_pic = request.files["profile_pic"]

        # get the file extension
        filename = raw_profile_pic.filename
        file_extension = path.splitext(filename)[1][1:]

        # if the file is in an allowed format
        if file_extension not in ALLOWED_EXTENSIONS:
            flash("Wrong format of image", "error")
            return redirect(url_for("change_pic"))

        # check if a file was uploaded
        if raw_profile_pic:
            # create a secure filename
            filename = secure_filename(raw_profile_pic.filename)
            unique_filename = str(uuid.uuid1()) + "." + filename

            # get the upload folder
            upload_folder = current_app.config["UPLOAD_FOLDER"]
            # get the full path of where to save the file
            full_path = path.join(upload_folder, unique_filename)

            # Check if the upload folder exists, create it if not
            if not path.exists(upload_folder):
                makedirs(upload_folder)

            # Save the file
            raw_profile_pic.save(full_path)

            # set the new proile picture for the user
            current_user.profile_pic = unique_filename

            db.session.commit()
            flash("Profile picture updated successfully!", "success")

            return redirect(url_for("main.profile"))

        # if no file is uploaded
        else:
            flash("No file selected", "error")

    return render_template("change_pic.html", form=form)


@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.home"))
