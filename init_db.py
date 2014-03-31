#!/usr/bin/env python

"""This script creates sqlite DB and populates it with some data
Spec. tells us that there should be SQL scripts, so let it be SQL scripts."""

import sqlite3
from urlparse import urlparse
from config import SQLALCHEMY_DATABASE_URI

DB_FILE = urlparse(SQLALCHEMY_DATABASE_URI).path


create_tables = ("""CREATE TABLE book (
    id INTEGER NOT NULL, 
    title VARCHAR NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (title)
)""", 
"""CREATE TABLE author (
    id INTEGER NOT NULL, 
    name VARCHAR NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (name)
)""",
"""CREATE TABLE association (
    book_id INTEGER, 
    author_id INTEGER, 
    FOREIGN KEY(book_id) REFERENCES book (id), 
    FOREIGN KEY(author_id) REFERENCES author (id),
    UNIQUE (book_id, author_id)
)""")


books = [
    {'title' : "Linux Administration Handbook (2nd Edition)",
    "authors" : ["Evi Nemeth", "Garth Snyder", "Trent R. Hein"]},
    {'title' : "UNIX System Administration Handbook (3rd Edition)",
    'authors' : ["Evi Nemeth", "Garth Snyder", "Scott Seebass", "Trent R. Hein"]},
    {'title' : "UNIX System Administration Handbook (Bk\CD ROM) (2nd Edition)",
    'authors' : ["Evi Nemeth", "Garth Snyder","Scott Seebass", "Trent R. Hein"]},
    {'title' : "The Hobbit",
    "authors" : ["J.R.R.Tolkein",]},
    {'title' : "The Lord of the Rings Novel",
    "authors" : ["J.R.R.Tolkein",]},
    {'title' : "The Unfinished Tales",
    "authors" : ["J.R.R.Tolkein",]},
    {'title' : "The Adventures of Tom Bombadil",
    "authors" : ["J.R.R.Tolkein",]},
    {'title' : "White Fang",
    "authors" : ["Jack London",]},
    {'title' : "The Call of the Wild",
    "authors" : ["Jack London",]},
    {'title' : "The Sea Wolf",
    "authors" : ["Jack London",]},
    {'title' : "To Build a Fire",
    "authors" : ["Jack London",]},
    ]


def connect_to_db(db_name):
  conn = sqlite3.connect(db_name)
  curs = conn.cursor()
  return conn, curs


def init_db(conn, curs):
    # create tables
    curs.execute('DROP TABLE IF EXISTS association')
    curs.execute('DROP TABLE IF EXISTS book')
    curs.execute('DROP TABLE IF EXISTS author')
    for create_table in create_tables:
        curs.execute(create_table)
    # populating the DB with data
    for book in books:
        # adding book
        try:
            curs.execute('INSERT INTO book (title) VALUES (?)', (book['title'],))
            book_id = curs.lastrowid
        # this will fire if we already have this book in our DB
        except sqlite3.IntegrityError:
            curs.execute('SELECT book.id FROM book WHERE book.title = ?', (book['title'],))
            book_id = curs.fetchone()[0]
        for author in book['authors']:
            try:
                curs.execute('INSERT INTO author (name) VALUES (?)', (author,))
                author_id = curs.lastrowid
            # this will fire if we already have this author in our DB
            except sqlite3.IntegrityError:
                curs.execute('SELECT author.id FROM author WHERE author.name = ?', (author,))
                author_id = curs.fetchone()[0]
            # adding relationship
            try:
                curs.execute('INSERT INTO association (book_id, author_id) VALUES (?, ?)',
                             (book_id, author_id))
            except sqlite3.IntegrityError:
                pass
    conn.commit()


if __name__ == '__main__':
    init_db(*connect_to_db(DB_FILE))
    print "All done"