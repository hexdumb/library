from flask.ext.wtf import Form
from wtforms import fields, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField

from .models import Book, Author

class BookForm(Form):
    book_id = fields.HiddenField()
    title = fields.StringField(validators=[validators.required()])
    authors = QuerySelectMultipleField(query_factory=lambda: Author.query.all())

    def validate_title(form, field):
        """book title validator, will fail if book with such title is present in the DB"""
        match_books =  Book.query.filter_by(title=field.data).all()
        if form.book_id.data:
            for book in match_books:
                if str(book.id) != str(form.book_id.data):
                    raise validators.StopValidation("Duplicate Name")
        elif match_books:
            raise validators.StopValidation("Duplicate Name")


# This is some sort of a dirty hack
# It's impossible to set default values for QuerySelectMultipleField
# fields. So we'll use this form for editing when we should save currently 
# selected options
# Additional hack is using BookFormEdit.choices set
# to update variants on every form construction
class BookFormEdit(Form):
    book_id = fields.HiddenField()
    title = fields.StringField(validators=[validators.required()])
    choices = set([])
    authors = fields.SelectMultipleField(choices=choices)

    def __init__(self, *args, **kargs):
        choices = set([(str(a.id), a.name) for a in Author.query.all()])
        BookFormEdit.choices.update(choices)
        Form.__init__(self, *args, **kargs)


class AuthorForm(Form):
    author_id = fields.HiddenField()
    name = fields.StringField(validators=[validators.required()])
    books = QuerySelectMultipleField(query_factory=lambda: Book.query.all())

    def validate_name(form, field):
        """author name validator, will fail if such author is present in the DB"""
        match_authors = Author.query.filter_by(name=field.data).all()
        if form.author_id.data:
            for author in match_authors:
                if str(author.id) != str(form.author_id.data):
                    raise validators.StopValidation("Duplicate Name")
        elif match_authors:
            raise validators.StopValidation("Duplicate Name")

# This is some sort of a dirty hack
# It's impossible to set default values for QuerySelectMultipleField
# fields. So we'll use this form for editing when we should save currently 
# selected options
# Additional hack is using BookFormEdit.choices set
# to update variants on every form construction
class AuthorFormEdit(Form):
    author_id = fields.HiddenField()
    name = fields.StringField(validators=[validators.required()])
    choices = set([])
    books = fields.SelectMultipleField(choices=choices)

    def __init__(self,  *args, **kargs):
        choices = set([(str(a.id), a.title) for a in Book.query.all()])
        AuthorFormEdit.choices.update(choices)
        Form.__init__(self, *args, **kargs)


class HiddenForm(Form):
    """Form with hidden field which can be used to avoid CSRF attacks"""
    record_id = fields.HiddenField()