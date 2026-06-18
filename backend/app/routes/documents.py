from flask import Blueprint
from app.controllers.document_get import list_documents, get_document_by_id
from app.middlewares.auth import token_required


document_bp = Blueprint("document", __name__, url_prefix="/document")


# 2. Rota: GET /documents (Listagem paginada e filtrada)
@document_bp.get("/")
@token_required
def route_list_documents(current_user):
    return list_documents(current_user)


# 3. Rota: GET /documents/{document_id} (Metadados de um documento individual)
@document_bp.get("/<uuid:document_id>")
@token_required
def route_get_document_by_id(current_user, document_id):
    return get_document_by_id(current_user, document_id)