import os

from dotenv import load_dotenv
from flask import Flask # type: ignore[import]
from flask_migrate import Migrate # type: ignore[import]

from app.config.database import db # type: ignore[import]

load_dotenv()

from app.models import *

migrate = Migrate()

def create_app():

    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # Registra os blueprints
    from app.routes.auth import auth_bp
    from app.routes.health import health_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(health_bp)

    return app
