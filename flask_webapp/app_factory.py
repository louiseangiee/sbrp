from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config, TestingConfig

db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)

    if config_name == "testing":
        app.config.from_object(TestingConfig)

    db.init_app(app)

    # Import and register your blueprints, set up other configurations, etc.

    return app
