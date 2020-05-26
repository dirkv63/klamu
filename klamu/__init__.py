# import os
from config import Config
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from klamu.lib import my_env
# from klamu.lib.db_model import *

bootstrap = Bootstrap()
db = SQLAlchemy()
lm = LoginManager()
lm.login_view = 'main.login'


def create_app(config_class=Config):
    """
    Create an application instance.

    :param config_class: Pointer to the config class.
    :return: the configured application object.
    """

    app = Flask(__name__)

    # import configuration
    app.config.from_object(config_class)

    # Configure Logger, except for Test
    if not app.testing:
        hdl = my_env.init_loghandler(__name__)
        app.logger.addHandler(hdl)

    app.logger.info("Start Application")

    # initialize extensions
    bootstrap.init_app(app)
    db.init_app(app)
    lm.init_app(app)

    # import blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    # app.register_error_handler(404, page_not_found) - or use decorator

    # add Jinja Filters
    app.jinja_env.filters['datestamp'] = my_env.datestamp
    app.jinja_env.filters['datetimestamp'] = my_env.datetimestamp

    return app
