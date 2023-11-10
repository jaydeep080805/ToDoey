from . import db
from flask_login import UserMixin
from sqlalchemy import ForeignKey, Boolean
from datetime import date


class TaskDataBase(db.Model):
    # TODO add a description option so you can make a popout menu to edit the task
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("user_information.id"), nullable=False)
    task = db.Column(db.String(), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    category = db.Column(db.String())
    completed = db.Column(Boolean, default=False)
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
