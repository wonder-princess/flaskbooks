import email

from apps.app import db
from apps.crud.models import User
from flask import Blueprint, render_template

crud = Blueprint(
    "crud",
    __name__,
    template_folder="templates",
    static_folder="static",
)

@crud.route("/")
def index():
    return render_template("crud/index.html")

@crud.route("/sql")
def sql():
    db.session.query(User).all()
    return "コンソールログを確認してください"

@crud.route("/insert")
def insert():
    user = User(
        username="aaaa",
        email="maillllll",
        password="8888"
    )
    db.session.add(user)
    db.session.commit()
    return "1件追加しました"
