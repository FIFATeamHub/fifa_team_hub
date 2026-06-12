from flask import request, jsonify
from app.config.database import db
from app.models.document import Document
from app.models.audit_log import AuditLog
from app.models.enums.user_role import TypeDocument, LogAction
from app.services.document import validate_file
from uuid import UUID
from datetime import datetime, timezone


UUID_ZERADO = UUID("00000000-0000-0000-0000-000000000000") # UTILIZADO QUANDO OCORRER ERRO, PARA REGISTRAR O LOG DE FALHA


def register_audit_log(user_id_e, action_e, status_e, resource_id_e, date_event, details_e = None):

    try :

        log_falha = AuditLog(
            user_id = user_id_e,
            action=action_e,
            resource_id = resource_id_e,
            ip_address = request.remote_addr or "0.0.0.0",
            status = status_e,
            details = details_e,
            created_at=date_event

        )

        db.session.add(log_falha)
        db.session.commit()

    except Exception as log_err:
        
        db.session.rollback()
        print(f"Erro crítico ao tentar salvar Log de Auditoria: {log_err}")




def upload_document(current_user):

    ###################################

    # Analisar lógica de role

    ###################################

    momento_requisicao = datetime.now(timezone.utc)


    if 'file' not in request.files:
        erro_msg = "Nenhum arquivo enviado no campo 'file' "
        register_audit_log(current_user.id, LogAction.UPLOAD, "FAILURE", UUID_ZERADO, momento_requisicao, erro_msg)
        return jsonify({"error" : erro_msg}) , 400
    
    arquivo_fisico = request.files['file']
    tipo_texto = request.form.get('doc_type')


    if not tipo_texto:
        erro_msg = "O campo 'doc_type' é obrigatório"
        register_audit_log(current_user.id, LogAction.UPLOAD, "FAILURE", UUID_ZERADO, momento_requisicao, erro_msg)
        return jsonify({"error" : erro_msg}) , 400
    

    try: 
        tipo_documento_enum = TypeDocument(tipo_texto)

    except ValueError:
        erro_msg = f"O valor '{tipo_texto}' não é um tipo de documento válido do Enum"
        register_audit_log(current_user.id, LogAction.UPLOAD, "FAILURE", UUID_ZERADO, momento_requisicao, erro_msg)
        return jsonify({"error": erro_msg, "details": erro_msg}), 422
    

    sucesso, metadados_seguranca = validate_file(arquivo_fisico) # Chama a função no service que valida o MIME, extensão e tamanho


    if not sucesso :

        erro_msg = metadados_seguranca["error"]
        status_http = metadados_seguranca["status_code"]

        register_audit_log(current_user.id, LogAction.UPLOAD, "FAILURE", UUID_ZERADO, momento_requisicao, f"Falha de validação de segurança ({status_http}): {erro_msg}")

        return jsonify({"error": erro_msg, "details": erro_msg}), status_http
    

    tamanho_kb = metadados_seguranca["file_size_kb"]

    try:

        nome_original = arquivo_fisico.filename
        extensao = nome_original.split('.')[-1].lower()

        novo_documento = Document(
            selection_id=current_user.selection_id,
            uploaded_by=current_user.id,
            type=tipo_documento_enum,
            filename="provisorio", 
            storage_url="provisorio",
            created_at=momento_requisicao
        )

        nome_unico_arquivo = f"{novo_documento.id}.{extensao}"
        caminho_armazenamento = f"backend/storage/uploads/{current_user.selection_id}/{nome_unico_arquivo}"

        novo_documento.filename = nome_unico_arquivo
        novo_documento.storage_url = caminho_armazenamento

        db.session.add(novo_documento)
        db.session.flush()


        novo_log_sucesso = AuditLog(
            user_id=current_user.id,
            action=LogAction.UPLOAD,
            resource_id=novo_documento.id,
            ip_address=request.remote_addr or "0.0.0.0",
            status="SUCCESS",
            details="Upload realizado e metadados persistidos com sucesso",
            created_at=momento_requisicao 
        )


        db.session.add(novo_log_sucesso)
        db.session.commit()


        return jsonify({
            "id": str(novo_documento.id),
            "original_name": nome_original,
            "doc_type": novo_documento.type.value,
            "file_size_kb": tamanho_kb,
            "status": "PENDING",
            "uploaded_by": str(novo_documento.uploaded_by),
            "created_at": momento_requisicao.isoformat()
        }), 201
    

    except Exception as e:
        db.session.rollback()
        print(f"Erro no banco de dados durante upload: {e}")
        
        # Loga a quebra crítica de banco de dados com o datetime original
        register_audit_log(current_user.id, LogAction.UPLOAD, "FAILURE", UUID_ZERADO, momento_requisicao, f"Erro interno de banco de dados ao salvar documento: {str(e)}")

        return jsonify({"error": "Erro interno ao salvar arquivo", "details": str(e)}), 500

