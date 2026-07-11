import os
import re

from app.config import check_required_env_vars


from dotenv import load_dotenv
from pathlib import Path
from flask import Flask, jsonify, request  # type: ignore[import]
from flask_migrate import Migrate  # type: ignore[import]
from werkzeug.exceptions import HTTPException

from app.routes.auth import auth_bp
from app.extensions import cors, db, migrate, limiter

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from app.models import *

migrate = Migrate()

# Cobre localhost e faixas de IP privado (RFC1918), usado apenas quando nenhuma
# origem explícita é injetada (ambiente de dev, testando a partir de outro
# dispositivo na mesma rede local).
LOCAL_NETWORK_ORIGIN_REGEX = re.compile(
    r"^https?://(localhost|127\.0\.0\.1"
    r"|10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    r"|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}"
    r"|192\.168\.\d{1,3}\.\d{1,3}):\d+$"
)

def create_app(test_config=None):

    app = Flask(__name__)

    app.config["STORAGE_BACKEND"] = os.getenv("STORAGE_BACKEND", "local")
    app.config["LOCAL_STORAGE_PATH"] = os.getenv("LOCAL_STORAGE_PATH", "./storage/uploads")
    app.config["GCS_BUCKET_NAME"] = os.getenv("GCS_BUCKET_NAME")
    app.config["GCP_PROJECT_ID"] = os.getenv("GCP_PROJECT_ID")
    app.config["GCS_PUBLIC_URL"] = os.getenv("GCS_PUBLIC_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_EXPIRE_ON_COMMIT"] = False

    if test_config:
        app.config.update(test_config)

    if not app.config.get("TESTING"):
        check_required_env_vars()

    is_prod = bool(os.getenv("GOOGLE_CLOUD_PROJECT"))
    if is_prod:
        from app.services.gcp_secrets import get_secret
        import urllib.parse
        
        app.config["SECRET_KEY"] = get_secret("JWT_SECRET_KEY")
        app.config["JWT_SECRET_KEY"] = get_secret("JWT_SECRET_KEY")
        
        db_user = os.getenv("DB_USER", "postgres")
        raw_pass = get_secret("DB_PASSWORD")
        db_pass = urllib.parse.quote_plus(raw_pass)
        db_name = os.getenv("DB_NAME", "postgres")
        db_instance_name = os.getenv("CLOUD_SQL_INSTANCE_NAME")
        app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql+psycopg2://{db_user}:{db_pass}@/{db_name}?host=/cloudsql/{db_instance_name}"
    else:
        app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
        app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

    if test_config:
        app.config.update(test_config)

    cors_env = os.getenv("CORS_ALLOWED_ORIGINS") or os.getenv("FRONTEND_URL")
    if cors_env:
        # Produção (ou dev com override explícito): usa estritamente o que foi injetado
        cors_origins = [origin.strip() for origin in cors_env.split(",") if origin.strip()]
    elif is_prod:
        # Produção sem variável configurada: não libera nenhuma origem
        cors_origins = []
    else:
        # Dev sem variável configurada: localhost fixo + qualquer IP de rede local,
        # para permitir testar o frontend a partir de outro dispositivo na mesma rede
        cors_origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            LOCAL_NETWORK_ORIGIN_REGEX,
        ]

    cors.init_app(
        app,
        resources={
            r"/*": {
                "origins": cors_origins
            }
        },
    )

    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

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

    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        # Deixa exceções HTTP (404, 401, 429, etc.) seguirem seu tratamento
        # normal do Flask — só exceções realmente não tratadas (bugs, erros
        # de banco, etc.) devem cair aqui.
        if isinstance(e, HTTPException):
            return e
        app.logger.exception(
            "Unhandled exception on %s %s", request.method, request.path
        )
        return jsonify({"error": "Internal server error"}), 500

    _tables_created = False

    @app.before_request
    def setup_db_tables():
        nonlocal _tables_created
        if not _tables_created:
            try:
                db.create_all()
                _tables_created = True
            except Exception as e:
                app.logger.error(f"Erro ao criar tabelas no banco de dados: {e}")

    return app
