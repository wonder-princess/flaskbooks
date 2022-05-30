import logging

from email_validator import EmailNotValidError, validate_email
from flask import (Flask, current_app, flash, g, redirect, render_template,
                   request, url_for)
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.debug = True

app.config["SECRET_KEY"] = "v9dQLQ4AuZthAwAmFWEX"
app.logger.setLevel(logging.DEBUG)
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
toolbar = DebugToolbarExtension(app)

ctx = app.app_context()
ctx.push()
print(current_app.name)
g.connection = "connection"
print(g.connection)

@app.route('/')
def hello():
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

        flash("お問い合わせありがとうございました")
        return redirect(url_for("contact_complete"))
        
    return render_template("contact_complete.html")

with app.test_request_context("/users?updated=true"):
    print(request.args.get("updated"))
