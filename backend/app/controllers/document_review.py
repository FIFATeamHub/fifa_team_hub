from flask import request, jsonify
from app.extensions import db
from app.models.document import Document
from app.models.enums.user_role import UserRole, TypeDocument, DocStatus, LogAction
from app.services.audit import register_audit_log
from datetime import datetime
from zoneinfo import ZoneInfo
import traceback

def review_document(current_user, document_id):
    fuso_sp = ZoneInfo("America/Sao_Paulo") 
    momento_requisicao = datetime.now(fuso_sp)

    data = request.get_json()
    if not data or "status" not in data:
        return jsonify({"error": "O campo 'status' é obrigatório no corpo da requisição."}), 400

    novo_status_texto = data["status"]
    if novo_status_texto not in [DocStatus.APPROVED.value, DocStatus.REJECTED.value]:
        return jsonify({"error": f"Status '{novo_status_texto}' inválido. Deve ser APPROVED ou REJECTED."}), 400
    
    motivo = data.get("reason", "")

    try:
        documento = Document.query.get(document_id)

        if not documento:
            return jsonify({"error": "Documento não encontrado."}), 404
        
        # Só podemos revisar documentos PENDING
        if documento.status != DocStatus.PENDING.value:
            return jsonify({"error": f"Apenas documentos PENDING podem ser revisados. Status atual: {documento.status}."}), 400

        # Regra de negócio: não é possível revisar o próprio documento
        if documento.uploaded_by == current_user.id:
            register_audit_log(
                current_user.id, 
                LogAction.REVIEW, 
                "FAILURE", 
                document_id, 
                momento_requisicao, 
                "Tentativa de autorevisão bloqueada", 
                selection_id_e=current_user.selection_id
            )
            return jsonify({"error": "Acesso negado. Não é possível revisar um documento enviado por você mesmo."}), 403

        # Regras de permissão por tipo de documento
        if documento.type == TypeDocument.PASSPORT and current_user.role != UserRole.AUDITOR:
            return jsonify({"error": "Apenas AUDITOR pode revisar Passaportes."}), 403
        
        if documento.type == TypeDocument.LAUDO_MEDICO and current_user.role != UserRole.MEDICAL_STAFF:
            return jsonify({"error": "Apenas MEDICAL_STAFF pode revisar Laudos Médicos."}), 403

        # Atualiza os dados de revisão do documento
        documento.status = novo_status_texto
        documento.reviewed_by = current_user.id
        documento.reviewed_at = momento_requisicao

        db.session.commit()

        detalhes_log = f"Documento revisado para {novo_status_texto}."
        if motivo:
            detalhes_log += f" Motivo: {motivo}"

        register_audit_log(
            current_user.id,
            LogAction.REVIEW,
            "SUCCESS",
            document_id,
            momento_requisicao,
            detalhes_log,
            selection_id_e=current_user.selection_id
        )

        return jsonify({
            "message": f"Documento revisado com sucesso. Novo status: {novo_status_texto}",
            "id": str(documento.id),
            "status": documento.status,
            "reviewed_by": str(documento.reviewed_by),
            "reviewed_at": documento.reviewed_at.isoformat()
        }), 200

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        register_audit_log(
            current_user.id, 
            LogAction.REVIEW, 
            "FAILURE", 
            document_id, 
            momento_requisicao, 
            f"Erro interno: {str(e)}", 
            selection_id_e=current_user.selection_id
        )
        return jsonify({"error": "Erro interno ao processar a revisão do documento"}), 500
