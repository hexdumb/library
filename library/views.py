from functools import wraps

from flask import current_app, Blueprint, flash, redirect, render_template, url_for, session, request, abort, jsonify

from .forms import BookForm, BookFormEdit, AuthorForm, AuthorFormEdit, HiddenForm
from .models import db, Book, Author

library = Blueprint("library", __name__)

def login_required(F):
    """User login check decorator"""
    @wraps(F)
    def _F(*args, **kargs):
        if not session.get('logged_in'):
            abort(401)
        else:
            return F(*args, **kargs)
    return _F


def auth_required(F):
    """User authentication check decorator"""
    @wraps(F)
    def _F(*args, **kargs):
        if not session.get('auth'):
            abort(401)
        else:
            return F(*args, **kargs)
    return _F


@library.route("/")
def view_index():
    return render_template("index.html")


@library.route("/books")
@auth_required
def list_books():
    query = Book.query.filter(Book.id >= 0)
    books = query.order_by(Book.title).all()
    return render_template("books_list.html", title="Books List", books=books)


@library.route("/authors")
@auth_required
def list_authors():
    query = Author.query.filter(Author.id >= 0)
    authors = query.order_by(Author.name).all()
    return render_template("authors_list.html", title="Authors List", authors=authors)


@library.route("/book/<int:book_id>")
@auth_required
def view_book(book_id=None):
    book = Book.query.get_or_404(book_id)
    title = "Book: " + book.title
    form = HiddenForm(record_id=book_id)
    return render_template("book.html", book=book, title=title, form=form)


@library.route("/delete_book", methods=("POST", ))
@login_required
def delete_book():
    form = HiddenForm()
    if form.validate_on_submit():
        book = Book.query.get_or_404(form.record_id.data)
        db.session.delete(book)
        db.session.commit()
        flash("The book had been removed")
        return redirect(url_for("library.list_books"))
    return render_template("validation_error.html", form=form)


@library.route("/update_book/<int:book_id>")
@login_required
def update_book_form(book_id):
    book = Book.query.get_or_404(book_id)
    book_form = BookFormEdit()
    book_form.book_id.default = book.id
    book_form.title.default = book.title
    book_form.authors.default = [a.id for a in book.authors]
    book_form.process()
    return render_template('add_book.html', form=book_form)


@library.route("/author/<int:author_id>")
@auth_required
def view_author(author_id=None):
    author = Author.query.get_or_404(author_id)
    title = "Author: " + author.name
    form = HiddenForm(record_id=author.id)
    return render_template("author.html", author=author, title=title, form=form)


@library.route("/delete_author", methods=("POST", ))
@login_required
def delete_author():
    form = HiddenForm()
    if form.validate_on_submit():
        author = Author.query.get_or_404(form.record_id.data)
        db.session.delete(author)
        db.session.commit()
        flash("The author had been removed")
        return redirect(url_for("library.list_authors"))
    return render_template("validation_error.html", form=form)


@library.route("/update_author/<int:author_id>")
@login_required
def update_author_form(author_id):
    author = Author.query.get_or_404(author_id)
    author_form = AuthorFormEdit()
    author_form.author_id.default = author.id
    author_form.name.default = author.name
    author_form.books.default = [b.id for b in author.books]
    author_form.process()
    return render_template('add_author.html', form=author_form)


@library.route("/add_book")
@login_required
def add_book_form():
    book_form = BookForm()
    return render_template('add_book.html', form=book_form)


@library.route("/add_book", methods=("POST", ))
@login_required
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        book = Book.query.get_or_404(form.book_id.data) if form.book_id.data else Book()
        form.populate_obj(book)
        if not book.id:
            db.session.add(book)
            flash_msg = "Added book"
        else:
            flash_msg = "Updated book"
        db.session.commit()
        flash(flash_msg)
        return redirect(url_for("library.view_book", book_id=book.id))
    return render_template("validation_error.html", form=form)


@library.route("/add_author")
@login_required
def add_author_form():
    author_form = AuthorForm()
    return render_template('add_author.html', form=author_form)


@library.route("/add_author", methods=("POST", ))
@login_required
def add_author():
    form = AuthorForm()
    if form.validate_on_submit():
        author = Author.query.get_or_404(form.author_id.data) if form.author_id.data else Author()
        form.populate_obj(author)
        if not author.id:
            db.session.add(author)
            flash_msg = "Added author"
        else:
            flash_msg = "Updated author"
        db.session.commit()
        flash(flash_msg)
        return redirect(url_for("library.view_author", author_id=author.id))
    return render_template("validation_error.html", form=form)


@library.route('/login', methods=('GET', 'POST'))
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == current_app.config['USERNAME'] and \
        request.form['password'] == current_app.config['PASSWORD']:
            session['logged_in'] = True
            session['auth'] = True
            flash('You were logged in')
        elif request.form['username']:
            session['auth'] = True
            flash('You were authorized')
        else:
            error = 'Wrong credentials'
            return render_template('login.html', error=error)
        return redirect(url_for('library.view_index'))
    return render_template('login.html', error=error)


@library.route('/logout')
def logout():
    if session.pop('logged_in', None): flash('You were logged out')
    if session.pop('auth', None): flash('You were unauthorized')
    return redirect(url_for('library.view_index'))


@library.route('/search')
@auth_required
def search_form():
    return render_template('search.html')


@library.route('/search', methods=('POST', ))
@auth_required
def search():
    if 'book_title' in request.form and request.form['book_title']:
        list = Book.query.filter(Book.title.contains(request.form['book_title']))
        return render_template("books_list.html", title="Found Books", books=list)
    elif 'author_name' in request.form and request.form['author_name']:
        list = Author.query.filter(Author.name.contains(request.form['author_name']))
        return render_template("authors_list.html", title="Found Authors", authors=list)
    error = "Need a parameter"
    return render_template('search.html', error=error)


@library.route('/search_book_api')
@auth_required
def search_book_api():
    req = request.args.get('term', 'test', type=str)
    list = Book.query.filter(Book.title.contains(req)).order_by(Book.title).limit(10)
    res_dict = dict([(str(b.id), b.title) for b in list])
    return jsonify(**res_dict)


@library.route('/search_author_api')
@auth_required
def search_author_api():
    req = request.args.get('term', 'test', type=str)
    list = Author.query.filter(Author.name.contains(req)).order_by(Author.name).limit(10)
    res_dict = dict([(str(a.id), a.name) for a in list])
    return jsonify(**res_dict)