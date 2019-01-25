from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required

from application import app, db
from application.auth.models import User
from application.auth.forms import LoginForm
from application.auth.forms import UserForm
from application.books.models import Book


@app.route("/auth/", methods=["GET"])
def auth_index():
    return render_template("auth/list.html", users = User.query.all())

@app.route("/auth/login/", methods = ["GET", "POST"])
def auth_login():
    if request.method == "GET":
        return render_template("auth/loginform.html", form = LoginForm())

    form = LoginForm(request.form)
    # validoinnit

    user = User.query.filter_by(username=form.username.data, password=form.password.data).first()
    if not user:
        return render_template("auth/loginform.html", form = form,
                    error = "No such username or password")


    login_user(user)
    return redirect(url_for("index"))

@app.route("/auth/logout/")
def auth_logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/auth/new/")
def auth_form():
    return render_template("auth/new.html", form = UserForm())

@app.route("/auth/", methods=["POST"])
def auth_create():
    u = User(request.form.get("name"), request.form.get("username"), request.form.get("password"))

    db.session().add(u)
    db.session().commit()
    return redirect(url_for("auth_index"))


@app.route("/auth/<username>/", methods=["GET"])
@login_required
def auth_info(username):

    user = User.query.filter_by(username=username).first_or_404()

    return render_template("auth/userinfo.html", user=user, books=user.mybooks)

@app.route("/books/<username>/<book_id>/", methods=["POST"])
@login_required
def books_set_read(username, book_id):

    book = Book.query.get(book_id)
    book.read = True
    db.session().commit()

    return redirect(url_for('auth_info', username=username))
