import os
from dotenv import load_dotenv

# Flask will load .env and .flaskenv, but running from gunicorn will not load, so add here to be sure.
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))
load_dotenv(os.path.join(basedir, '.flaskenv'))
# Be careful: Variable names need to be UPPERCASE


class Config(object):
    # Main
    SECRET_KEY = os.urandom(24)
    LOGDIR = os.environ["LOGDIR"]
    LOGLEVEL = os.environ["LOGLEVEL"]

    # SQL Config
    SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = False
    # pythonanywhere disconnects clients after 5 minutes idle time. Set pool_recycle to avoid disconnection
    # errors in the log: https://help.pythonanywhere.com/pages/UsingSQLAlchemywithMySQL (from: PythonAnywhere -
    # some tips for specific web frameworks: Flask
    SQLALCHEMY_POOL_RECYCLE = 280

    if os.environ.get("WTF_CSR_ENABLED"):
        WTF_CSRF_ENABLED = os.environ["WTF_CSR_ENABLED"]
    if os.environ.get("SERVER_NAME"):
        SERVER_NAME = os.environ["SERVER_NAME"]


class TestConfig(Config):
    TESTING = True
