from flask import Flask

from .routes import init_app
from .extensions import db


def create_dev_app():
    app = Flask(__name__)
    app.config.from_object('app.config.DevelopmentConfig')
    db.init_app(app)
    init_app(app)
    return app

def create_prod_app():
    app = Flask(__name__)
    app.config.from_object('app.config.ProductionConfig')
    db.init_app(app)
    init_app(app)
    return app