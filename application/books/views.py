from flask import redirect, render_template, request, url_for
from flask_login import login_required, current_user

from application import app, db
from application.books.models import Book
from application.books.forms import BookForm
from application.authors.models import Author
from application.auth.models import User

@app.route("/books/", methods=["GET"])
def books_index():
    return render_template("books/list.html", books = Book.query.all())

@app.route("/books/new/")
@login_required
def books_form():
    return render_template("books/new.html", form = BookForm())


@app.route("/books/", methods=["POST"])
@login_required
def books_create():
    form = BookForm(request.form)

    if not form.validate():
        return render_template("books/new.html", form = form)

    book = Book(form.name.data)
    author = Author.query.filter_by(firstname=form.author_firstname.data).first()
    user = User.query.filter_by(username=current_user.username).first_or_404()

    book.read = form.read.data
    book.account_id = user.id
    book.author_id = author.id

    user.mybooks.append(book)
    author.books.append(book)
    db.session().add(book)
    db.session().commit()

    return redirect(url_for("books_index"))

