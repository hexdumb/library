from os.path import abspath, dirname, join

_cwd = dirname(abspath(__file__))

SECRET_KEY = 'flask-session-mega-secret-key'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + join(_cwd, 'library.db')
SQLALCHEMY_ECHO = True
WTF_CSRF_SECRET_KEY = 'this-should-be-something-random'

USERNAME = 'user'
PASSWORD = "pass"