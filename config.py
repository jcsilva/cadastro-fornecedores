import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BOOTSTRAP_SERVE_LOCAL = True # This turns file serving static
                                 # https://pythonhosted.org/Flask-Bootstrap/configuration.html
                                 # https://stackoverflow.com/questions/30185966/how-to-use-bootstrap-static-with-flask-bootstrap
