#!/usr/bin/env python


from library import app, db

if __name__ == "__main__":
    app.debug = True
    db.create_all(app=app)
    app.run()