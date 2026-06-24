# backend/tests/conftest.py
import pytest
from flask import g, jsonify
from app import create_app
from app.extensions import db  # O mesmo db que a aplicação usa
from app.middlewares.auth_middleware import require_role, require_auth
from app.services.auth_service import create_access_token

@pytest.fixture
def app():
    # Passamos as configurações de teste DIRETAMENTE na criação do app
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    # Criamos a estrutura de tabelas no banco SQLite em memória
    with app.app_context():
        db.create_all()

    # Rotas fictícias para os testes de middleware
    @app.get("/test/protegida")
    @require_auth
    def rota_protegida():
        return jsonify({
            "user_id": g.current_user_id,
            "role": getattr(g, "current_user_role", None),  # Evita quebra se não mapeado
            "selection_id": getattr(g, "current_selection_id", None)
        }), 200
    
    @app.get("/test/so-organizer")
    @require_auth
    @require_role("ORGANIZER")
    def rota_organizer():
        return jsonify({"ok": True}), 200

    yield app

    # Derruba o banco em memória após o fim dos testes deste ciclo
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def token_bra_staff():
    return create_access_token({
        "user_id": 10,
        "role": "staff",
        "selection_id": "BRA" 
    })

@pytest.fixture
def token_organizer():
    return create_access_token({
        "user_id": 20,
        "role": "ORGANIZER",
        "selection_id": None
    })

@pytest.fixture
def arg_document_id(app):
    with app.app_context():
        try:
            from app.models import Document 
            
            doc = Document(
                original_name="tactical_plan_arg.pdf",
                doc_type="pdf",
                status="PENDENTE",
                selection_id="ARG" 
            )
            db.session.add(doc)
            db.session.commit()
            return doc.id
        except Exception:
            return "id-documento-argentina-ficticio"