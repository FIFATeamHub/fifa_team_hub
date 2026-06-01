from flask import Blueprint

health_bp = Blueprint("health", __name__)

#criando a rota
@health_bp.get("/health")
def health():
    return {"status" : "ok", "service" : "fifa-team-hub"}, 200