import os

from dotenv import load_dotenv
from flask import Flask # type: ignore[import]
from flask_migrate import Migrate # type: ignore[import]


from app.config.database import db # type: ignore[import]

from flask_jwt_extended import JWTManager

load_dotenv()

from app.models import *

migrate = Migrate()

def create_app():
    
    from app.routes.auth import auth_bp

    app = Flask(__name__)

    

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    jwt = JWTManager(app) #inicializar

    app.register_blueprint(auth_bp, url_prefix='/auth')

    db.init_app(app)
    migrate.init_app(app, db)

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    return app
    