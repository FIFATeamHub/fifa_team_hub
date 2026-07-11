from flask import Blueprint
from app.middlewares.auth import token_required
from app.controllers.audit_logs import list_audit_logs

audit_bp = Blueprint("audit", __name__)

@audit_bp.route("/", methods=["GET"])
@token_required
def route_list_audit_logs(current_user):
    # Passa o usuário logado para o Controller avaliar se ele é AUDITOR
    return list_audit_logs(current_user)
