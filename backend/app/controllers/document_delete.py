from flask import jsonify
from datetime import datetime
from zoneinfo import ZoneInfo

from app.extensions import db
from app.models.document import Document
from app.models.enums.user_role import UserRole, LogAction
from app.controllers.document_upload import register_audit_log
from app.services.storage_factory import get_storage_service


def delete_document(current_user, document_id):

    document = Document.query.get(document_id)

    if document is None:
        return jsonify({"error": "Documento não encontrado"}), 404

    if current_user.role != UserRole.TECHNICAL_STAFF:
        return jsonify({"error": "Acesso negado"}), 403

    if document.uploaded_by != current_user.id:
        return jsonify({"error": "Você só pode excluir documentos enviados por você."}), 403

    if document.selection_id != current_user.selection_id:
        return jsonify({"error": "Documento pertence a outra seleção."}), 403

    storage = get_storage_service()

    if document.storage_url:
        storage.delete_file(document.storage_url)
    elif document.storage_path:
        storage.delete_file(document.storage_path)

    document.deleted_at = datetime.now(ZoneInfo("America/Sao_Paulo"))

    db.session.add(document)
    db.session.commit()

    register_audit_log(
        current_user.id,
        LogAction.DELETE,
        "SUCCESS",
        str(document.id),
        datetime.now(ZoneInfo("America/Sao_Paulo")),
        "Documento removido."
    )

    return "", 204