from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

from application import app, db
from application.auth.models import User
from application.auth.models import users_books
from application.auth.forms import LoginForm
from application.auth.forms import UserForm
from application.books.models import Book

from sqlalchemy.sql import text


@app.route("/auth/", methods=["GET"])
def auth_index():
    return render_template("auth/list.html", users=User.query.all())


@app.route("/auth/login/", methods=["GET", "POST"])
def auth_login():
    if request.method == "GET":
        return render_template("auth/loginform.html", form=LoginForm())

    form = LoginForm(request.form)
    # validoinnit

    user = User.query.filter_by(username=form.username.data, password=form.password.data).first()
    if not user:
        return render_template("auth/loginform.html", form=form,
                               error="No such username or password")

    login_user(user)
    return redirect(url_for("index"))


@app.route("/auth/logout/")
@login_required
def auth_logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/auth/new/")
def auth_form():
    return render_template("auth/new.html", form=UserForm())


@app.route("/auth/", methods=["POST"])
def auth_create():
    u = User(request.form.get("name"), request.form.get("username"), request.form.get("password"))

    db.session().add(u)
    db.session().commit()
    return redirect(url_for("auth_login"))


@app.route("/auth/<username>/", methods=["GET"])
@login_required
def auth_info(username):
    user = User.query.filter_by(username=username).first()

    stmt = text(
        "SELECT ub.book_id, user_id, firstname, lastname, read, name FROM users_books ub, authors_books ab "
        "JOIN book b ON b.id=ub.book_id JOIN author ON author.id=ab.author_id WHERE ub.user_id=:user_id "
        "AND ab.book_id=ub.book_id;").params(
        user_id=user.id)

    bookslist = db.engine.execute(stmt)
    db.session().commit()

    return render_template("auth/userinfo.html", user=user, books=bookslist, all_books=user.count_all_books(user.id),
                           read_books=user.count_read_books(user.id))


@app.route("/auth/<username>/<book_id>/", methods=["POST"])
@login_required
def books_set_read_or_delete(username, book_id):
    user = User.query.filter_by(username=username).first()

    if request.form["btn"] == "Merkitse luetuksi":

        stmt = text("UPDATE users_books SET read = 1 WHERE book_id = :book_id AND user_id = :user_id") \
            .params(user_id=user.id, book_id=book_id)

    elif request.form["btn"] == "Merkitse lukemattomaksi":
        stmt = text("UPDATE users_books SET read = 0 WHERE book_id = :book_id AND user_id = :user_id") \
            .params(user_id=user.id, book_id=book_id)

    else:
        stmt = text("DELETE FROM users_books WHERE user_id = :user_id AND book_id = :book_id") \
            .params(user_id=user.id, book_id=book_id)

    db.engine.execute(stmt)
    db.session().commit()

    return redirect(url_for("auth_info", username=username))

@app.route("/auth/edit/", methods=["GET", "POST"])
@login_required
def auth_edit_form():

    if request.method == "GET":
        return render_template("auth/editinfo.html", form=UserForm())

    else:
        modifieduser = User(request.form.get("name"), request.form.get("username"), request.form.get("password"))
        if modifieduser.name != "":
            current_user.name = modifieduser.name

        if modifieduser.username != "":
            current_user.username = modifieduser.username

        if modifieduser.password != "":
            current_user.password = modifieduser.password

        db.session().commit()
        return redirect(url_for('auth_info', username=current_user.username))

