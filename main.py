from flask import Flask, render_template, url_for, request

app = Flask(__name__)
app.secret_key = "roboExtreme"


@app.route("/")
def main_page():
    return render_template("main_page.html")


if __name__ == "__main__":
    app.run()
