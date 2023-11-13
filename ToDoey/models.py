from flask_login import UserMixin
from sqlalchemy import ForeignKey, Boolean
from datetime import date
from os import path
from . import db


basedir = path.abspath(path.dirname(__file__))


# Database model for user tasks
class TaskDataBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("user_information.id"), nullable=False)
    task = db.Column(db.String(), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    category = db.Column(db.String())
    completed = db.Column(Boolean, default=False)
    date_completed = db.Column(db.Date, nullable=True)
    user = db.relationship("UserInformation", back_populates="tasks")


# Database model for user information
class UserInformation(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False, index=True)
    password = db.Column(db.String(), nullable=False)
    profile_pic = db.Column(db.String(), default=f"{basedir}static/images/default.png")
    creation_date = db.Column(db.Date, default=date.today())
    wants_notifications = db.Column(db.Boolean, default=True)
    notification_type = db.Column(db.String(), default="email")
    notification_time = db.Column(db.String, default="1 hour")
    tasks = db.relationship(
        "TaskDataBase", order_by=TaskDataBase.due_date, back_populates="user"
    )
