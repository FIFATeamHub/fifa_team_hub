import os

from app.config import check_required_env_vars


from dotenv import load_dotenv
from pathlib import Path
from flask import Flask  # type: ignore[import]
from flask_migrate import Migrate  # type: ignore[import]

from app.routes.auth import auth_bp
from app.extensions import cors, db, migrate

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from app.models import *

migrate = Migrate()

def create_app(test_config=None):

    app = Flask(__name__)

    app.config["STORAGE_BACKEND"] = os.getenv("STORAGE_BACKEND", "local")
    app.config["LOCAL_STORAGE_PATH"] = os.getenv(
        "LOCAL_STORAGE_PATH",
        "./storage/uploads"
    )
    app.config["GCS_BUCKET_NAME"] = os.getenv("GCS_BUCKET_NAME")
    app.config["GCP_PROJECT_ID"] = os.getenv("GCP_PROJECT_ID")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_EXPIRE_ON_COMMIT"] = False

    if test_config:
        app.config.update(test_config)

    if not app.config.get("TESTING"):
        check_required_env_vars()
    
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

    db.init_app(app)
    migrate.init_app(app, db)

    # Registra os blueprints
    from app.routes.auth import auth_bp
    from app.routes.documents import document_bp
    from app.routes.health import health_bp
    from app.routes.selection import selection_bp
    from app.routes.audit import audit_bp

    app.register_blueprint(document_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(selection_bp)
    app.register_blueprint(audit_bp, url_prefix="/api/audit")

    
    return app
