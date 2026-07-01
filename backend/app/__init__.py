import os

from dotenv import load_dotenv
from pathlib import Path
from flask import Flask  # type: ignore[import]
from flask_migrate import Migrate  # type: ignore[import]


from app.config.database import db  # type: ignore[import]
from app.routes.auth import auth_bp
from app.extensions import cors, db, migrate

# O .env está na raiz do projeto, um nível acima de /backend
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from app.models import *

migrate = Migrate()

def create_app(test_config=None):

    app = Flask(__name__)


    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_EXPIRE_ON_COMMIT"] = False
    
    #CORS permite que o navegador do cliente faça requisições ao backend mesmo que frontend e backend estejam em origens diferentes.
    
    cors.init_app(
        app,
        resources={
            r"/*": {
                "origins": [
                    "http://localhost:5173",
                    "http://127.0.0.1:5173",
                    "http://localhost:5000",
                    "http://127.0.0.1:5000",
                ]
            }
        },
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Registra os blueprints
    from app.routes.auth import auth_bp
    from app.routes.documents import document_bp
    from app.routes.health import health_bp
    from app.routes.selection import selection_bp

    app.register_blueprint(document_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(selection_bp)
    
    return app
