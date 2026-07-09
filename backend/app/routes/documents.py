from flask import Blueprint
from app.controllers.document_get import list_documents, get_document_by_id, download_document_url, stream_local_file
from app.controllers.document_upload import upload_document
from app.middlewares.auth import token_required
from app.controllers.document_delete import delete_document

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




# Rota para obter o link agnóstico de download
@document_bp.get("/<uuid:document_id>/download")
@token_required
def route_download_document_url(current_user, document_id):
    return download_document_url(current_user, document_id)




# Rota interna de streaming (acionada apenas quando o storage for local)
@document_bp.get("/<uuid:document_id>/stream")
@token_required
def route_stream_local_file(current_user, document_id):
    return stream_local_file(current_user, document_id)




@document_bp.post("/upload")
@token_required
def upload_documento(current_user):
    return upload_document(current_user)

# 5. Rota: DELETE /api/documents/{document_id} (Adicionada para o teste de exclusão)
@document_bp.delete("/<uuid:document_id>")
@token_required
def route_delete_document(current_user, document_id):
    return delete_document(current_user, document_id)
