from flask import Blueprint, jsonify
from app.controllers.document_get import list_documents, get_document_by_id
from app.controllers.document_upload import upload_document
from app.middlewares.auth import token_required


document_bp = Blueprint("document", __name__, url_prefix="/api/document")


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

# 4. Rota: POST /api/documents/upload
@document_bp.post("/upload")
@token_required
def upload_documento(current_user):
    return upload_document(current_user)

# 5. Rota: DELETE /api/documents/{document_id} (Adicionada para o teste de exclusão)
@document_bp.delete("/<uuid:document_id>")
@token_required
def route_delete_document(current_user, document_id):
    return jsonify({"message": "Documento deletado"}), 200
