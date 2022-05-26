from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    name = "Hello World"
    return name

@app.route('/good')
def good():
    name = "Good"
    return name

## おまじない
if __name__ == "__main__":
    app.run(debug=True)

@app.route("/hoget",
    methods=["GET"],
    endpoint="hoget-endpoint")
def hoget():
    return "hoge"

@app.route("/<foo>",
    methods=["GET", "POST"],
    endpoint="foo-endpoint")
def foo(foo):
    return f"{foo}"
