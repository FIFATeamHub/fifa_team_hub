from flask import jsonify
from datetime import datetime
from zoneinfo import ZoneInfo

from app.extensions import db
from app.models.document import Document
from app.models.enums.user_role import UserRole, LogAction
from app.controllers.document_upload import UUID_ZERADO
from app.services.audit import register_audit_log
from app.services.storage_factory import get_storage_service


def delete_document(current_user, document_id):

    document = db.session.get(Document, document_id)

    if document is None:
        return jsonify({"error": "Documento não encontrado"}), 404

    papeis_que_podem_excluir = [UserRole.TECHNICAL_STAFF, UserRole.AUDITOR, UserRole.MEDICAL_STAFF, UserRole.ATHELETE]

    if current_user.role not in papeis_que_podem_excluir:
        register_audit_log(current_user.id, LogAction.DELETE, "ACCESS_DENIED", document.id, datetime.now(ZoneInfo("America/Sao_Paulo")), "Perfil sem permissão para excluir documentos.", selection_id_e=current_user.selection_id)
        return jsonify({"error": "Acesso negado"}), 403

    if document.uploaded_by != current_user.id:
        register_audit_log(current_user.id, LogAction.DELETE, "ACCESS_DENIED", document.id, datetime.now(ZoneInfo("America/Sao_Paulo")), "Tentativa de deletar documento de outro usuário.", selection_id_e=current_user.selection_id)
        return jsonify({"error": "Você só pode excluir documentos enviados por você."}), 403

    if document.selection_id != current_user.selection_id:
        register_audit_log(current_user.id, LogAction.DELETE, "ACCESS_DENIED", document.id, datetime.now(ZoneInfo("America/Sao_Paulo")), "Documento pertence a outra seleção.", selection_id_e=current_user.selection_id)
        return jsonify({"error": "Documento pertence a outra seleção."}), 403


    storage = get_storage_service()

    if document.storage_url:
        storage.delete_file(document.storage_url)
    elif document.storage_path:
        storage.delete_file(document.storage_path)

    document.deleted_at = datetime.now(ZoneInfo("America/Sao_Paulo"))
    document.status = "DELETED" 

    db.session.add(document)
    db.session.commit()

    register_audit_log(
        current_user.id,
        LogAction.DELETE,
        "SUCCESS",
        document.id,
        datetime.now(ZoneInfo("America/Sao_Paulo")),
        "Documento removido (Soft Delete e Storage Limpo).",
        selection_id_e=current_user.selection_id
    )

    return "", 204