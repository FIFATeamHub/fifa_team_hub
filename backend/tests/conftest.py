import pytest

from flask import g, jsonify
from app import create_app
from app.middlewares.auth_middleware import require_role, require_auth

@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True

    #usa banco em memoria - sem precisar do PostgreSQL nos testes
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    #rotas ficticias que existem somente durante os testes
    @app.get("/test/protegida")
    @require_auth
    def rota_protegida():
        return jsonify({
            "user_id" : g.current_user_id,
            "role" : g.current_role,
            #não precisa do selection id?
        }), 200
    
    @app.get("/test/so-organizer")
    @require_auth
    @require_role("ORGANIZER")
    def rota_organizer():
        return jsonify({"ok": True}), 200

    yield app

@pytest.fixture
def client(app):
    return app.test_client()
