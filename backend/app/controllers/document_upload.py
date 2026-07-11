from flask import request, jsonify
from app.extensions import db
from app.models.document import Document
from app.models.audit_log import AuditLog
from app.models.enums.user_role import TypeDocument, LogAction
from app.services.document import validate_file, validate_upload_permission
from app.services.storage_service import LocalStorageService
from app.services.storage_factory import get_storage_service
from app.services.audit import register_audit_log
from werkzeug.utils import secure_filename
from google.api_core.exceptions import ResourceExhausted
import uuid
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import traceback


UUID_ZERADO = uuid.uuid4()  # Sentinel para logs de falha sem recurso associado


def upload_document(current_user):

    fuso_sp = ZoneInfo("America/Sao_Paulo") 
    momento_requisicao = datetime.now(fuso_sp)


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
    

    permitido, status_documento = validate_upload_permission(current_user.role, tipo_documento_enum)

    if not permitido:
        erro_msg = f"Acesso negado. O perfil '{current_user.role}' não tem permissão para fazer upload de '{tipo_documento_enum.name}'."
        register_audit_log(current_user.id, LogAction.UPLOAD, "FAILURE", UUID_ZERADO, momento_requisicao, erro_msg)
        return jsonify({"error": "Acesso negado.", "details": erro_msg}), 403
    

    sucesso, metadados_seguranca = validate_file(arquivo_fisico) # Chama a função no service que valida o MIME, extensão e tamanho


    if not sucesso :

        erro_msg = metadados_seguranca["error"]
        status_http = metadados_seguranca["status_code"]

        register_audit_log(current_user.id, LogAction.UPLOAD, "FAILURE", UUID_ZERADO, momento_requisicao, f"Falha de validação de segurança ({status_http}): {erro_msg}")

        return jsonify({"error": erro_msg, "details": erro_msg}), status_http
    

    tamanho_kb = metadados_seguranca["file_size_kb"]

    try:

        nome_original = arquivo_fisico.filename

        nome_original_limpo = secure_filename(nome_original)

        extensao = nome_original.split('.')[-1].lower()

        id_exclusivo_doc = uuid.uuid4()

        # 2. Monte o nome único usando o UUID gerado
        extensao = nome_original.rsplit('.', 1)[1].lower() if '.' in nome_original else 'pdf'
        nome_unico_arquivo = f"{id_exclusivo_doc}.{extensao}"


        storage = get_storage_service()
        caminho_armazenamento = storage.save_file(
            file_stream=arquivo_fisico,
            stored_name=nome_unico_arquivo,
            selection_id=str(current_user.selection_id)
        )

        novo_documento = Document(
            selection_id=current_user.selection_id,
            uploaded_by=current_user.id,
            type=tipo_documento_enum,
            # filename=nome_unico_arquivo, 
            original_name= nome_original_limpo,
            storage_path=caminho_armazenamento,
            status=status_documento,
            created_at=momento_requisicao
        )


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
            "original_name": nome_original_limpo,
            "doc_type": novo_documento.type.value,
            "file_size_kb": tamanho_kb,
            "status": "PENDING",
            "uploaded_by": str(novo_documento.uploaded_by),
            "created_at": momento_requisicao.isoformat()
        }), 201
    
    except ResourceExhausted as e:
        db.session.rollback()
        register_audit_log(current_user.id, LogAction.UPLOAD, "FAILURE", UUID_ZERADO, momento_requisicao, f"Cota do storage excedida: {str(e)}")

        return jsonify({
            "error": "Serviço de armazenamento temporariamente indisponível (cota excedida).",
        }), 503

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        print(f"Erro no banco de dados durante upload: {e}")
        
        # Loga a quebra crítica de banco de dados com o datetime original
        register_audit_log(current_user.id, LogAction.UPLOAD, "FAILURE", UUID_ZERADO, momento_requisicao, f"Erro interno de banco de dados ao salvar documento: {str(e)}")

        return jsonify({
            "error": "Erro interno ao salvar documento",
        }), 500
