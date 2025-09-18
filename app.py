from flask import Flask, render_template, redirect, url_for

# eshadaaay
def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/login")
    def login():
        return render_template("login.html")

    @app.route("/student")
    def student():
        return render_template("student.html")

    @app.route("/teacher")
    def teacher():
        return render_template("teacher.html")

    @app.route("/subject")
    def subject():
        return render_template("subject.html")

    @app.route("/finance")
    def finance():
        return render_template("finance.html")

    @app.route("/hall")
    def hall():
        return render_template("hall.html")

    @app.route("/coach")
    def coach():
        return render_template("coach.html")

    @app.route("/lab")
    def lab():
        return render_template("lab.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)


