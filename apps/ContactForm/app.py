import logging
import os

from email_validator import EmailNotValidError, validate_email
from flask import (Flask, current_app, flash, g, redirect, render_template,
                   request, url_for)
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail, Message

app = Flask(__name__)
app.debug = True

app.config["SECRET_KEY"] = "v9dQLQ4AuZthAwAmFWEX"
app.logger.setLevel(logging.DEBUG)
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
toolbar = DebugToolbarExtension(app)

app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
app.config["MAIL_PORT"] = os.environ.get("MAIL_PORT")
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS")
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")

mail = Mail(app)

@app.route('/')
def index():
    return render_template("contact.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/contact/complete",
    methods=["GET", "POST"])
def contact_complete():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        desription = request.form["desription"]

        is_valid = True

        if not username:
            flash("ユーザー名は必須です")
            is_valid = False

        try:
            validate_email(email)
        except EmailNotValidError:
            flash("メールアドレスの形式で入力してください")
            is_valid = False

        if not email:
            flash("メールアドレスは必須です")
            is_valid = False

        if not desription:
            flash("問い合わせ内容は必須です")
            is_valid = False

        if not is_valid:
            return redirect(url_for("contact"))

        print("-----checked form-----")

        flash("お問い合わせありがとうございました")
        
        send_email(
            email,
            "お問い合わせありがとうございました。",
            "contact_mail",
            username=username,
            desription=desription,
        )

        return redirect(url_for("contact_complete"))
    return render_template("contact_complete.html")

def send_email(to, subject, template, **kwaargs):
    msg = Message(subject, recipients=[to])
    msg.body = render_template(template + ".txt", **kwaargs)
    msg.html = render_template(template + ".html", **kwaargs)
    mail.send(msg)
    print("-----success send mail-----")
