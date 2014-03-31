from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Assiciation table for many-to-many relationship
association_table = db.Table('association',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id')),
    db.Column('author_id', db.Integer, db.ForeignKey('author.id')),
    db.UniqueConstraint('book_id', 'author_id')
    )


class Book(db.Model):
    """Book table model"""
    __tablename__ = 'book'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)
    authors = db.relationship('Author', secondary=association_table,
        backref=db.backref('books', lazy='select'))

    def __repr__(self):
        return '<Book %r >' % (self.title)

    def __str__(self):
        return self.title


class Author(db.Model):
    """Author table model"""
    __tablename__ = 'author'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    def __repr__(self):
        return '<Author %r >' % (self.name)

    def __str__(self):
        return self.name