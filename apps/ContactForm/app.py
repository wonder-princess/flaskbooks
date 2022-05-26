from flask import (Flask, current_app, g, redirect, render_template, request,
                   url_for)

app = Flask(__name__)

@app.route('/')
def hello():
    name = "Hello World"
    return name

@app.route("/contact")
def contact():
    return render_template("contact.html")

app.route("/contact/complete",
    methods=["GET", "POST"])
def contact_complete():
    if request.method == "POST":



        return redirect(url_for("contact_complete"))
    return render_template("contact_complete.html")

## おまじない
if __name__ == "__main__":
    app.run(debug=True)

