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

    app.config.from_object('app.config.Config')
    
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

    
    return app
