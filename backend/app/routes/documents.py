from flask import Blueprint

from app.controllers.document_upload import upload_document
from app.middlewares.auth import token_required

document_bp = Blueprint("document", __name__, url_prefix="/document")

@document_bp.get("/")
@token_required
def listar_documentos(current_user):
    return ...


@document_bp.post("/upload")
@token_required
def upload_documento(current_user):
    return upload_document(current_user)