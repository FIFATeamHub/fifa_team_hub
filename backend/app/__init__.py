import os

from app.config import check_required_env_vars


from dotenv import load_dotenv
from pathlib import Path
from flask import Flask  # type: ignore[import]
from flask_migrate import Migrate  # type: ignore[import]





from app.routes.auth import auth_bp
from app.extensions import cors, db, migrate

# O .env está na raiz do projeto, um nível acima de /backend
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from app.models import *

migrate = Migrate()

def create_app(test_config=None):

    app = Flask(__name__)

    check_required_env_vars()

    app.config["STORAGE_BACKEND"] = os.getenv("STORAGE_BACKEND", "local")
    app.config["LOCAL_STORAGE_PATH"] = os.getenv("LOCAL_STORAGE_PATH", "./storage/uploads")
    app.config["GCS_BUCKET_NAME"] = os.getenv("GCS_BUCKET_NAME")
    app.config["GCP_PROJECT_ID"] = os.getenv("GCP_PROJECT_ID")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_EXPIRE_ON_COMMIT"] = False

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
        app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "local_fallback_secret")
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    
    #CORS permite que o navegador do cliente faça requisições ao backend mesmo que frontend e backend estejam em origens diferentes.
    
    cors.init_app(
        app,
        resources={
            r"/*": {
                "origins": "*"
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
    from app.routes.audit import audit_bp

    app.register_blueprint(document_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(selection_bp)
    app.register_blueprint(audit_bp, url_prefix="/api/audit")

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
