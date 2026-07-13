from flask import jsonify, request
from flask import send_file
import os
from app.services.document_get import DocumentService
from app.models.enums.user_role import  LogAction
from app.controllers.document_upload import UUID_ZERADO
from app.services.audit import register_audit_log
from app.services.storage_factory import get_storage_service
from google.cloud.exceptions import NotFound
from datetime import datetime, timezone
from zoneinfo import ZoneInfo




def list_documents(current_user):
    doc_type_filter = request.args.get("doc_type")
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    # 2. CHAMA O SERVICE para processar as regras de banco
    paginated_result = DocumentService.list_accessible_documents(
        current_user=current_user,
        doc_type_filter=doc_type_filter,
        page=page,
        per_page=per_page
    )

    # Se o perfil for inválido ou não autorizado, o service retorna None
    if paginated_result is None:
        fuso_sp = ZoneInfo("America/Sao_Paulo") 
        momento_requisicao = datetime.now(fuso_sp)
        register_audit_log(current_user.id, LogAction.ACCESS_DENIED , "FAILURE", UUID_ZERADO ,momento_requisicao, "Acesso negado. Perfil inválido.", selection_id_e=current_user.selection_id)
        return jsonify({"error": "Acesso negado. Perfil inválido."}), 403

    # 3. FORMATAÇÃO DO JSON DE RETORNO (Higienização de dados)
    data_list = []
    for doc in paginated_result.items:
        data_list.append({
            "id": str(doc.id),
            "original_name": doc.original_name,
            "doc_type": doc.type.value if hasattr(doc.type, "value") else str(doc.type),
            "storage_url": doc.storage_url,
            "status": doc.status,
            "uploaded_by_id": str(doc.uploaded_by),
            "selection_code": doc.selection.code if doc.selection else None,
            "created_at": doc.created_at.isoformat() + "Z" if doc.created_at else None
        })

    # 4. RETORNO DA ESTRUTURA COMPLETA PAGINADA
    return jsonify({
        "data": data_list,
        "pagination": {
            "page": paginated_result.page,
            "per_page": paginated_result.per_page,
            "total": paginated_result.total,
            "pages": paginated_result.pages
        }
    }), 200
    
    
def list_pending_documents(current_user):
    """
    Retorna os tipos de documentos obrigatórios
    que o usuário autenticado ainda precisa enviar.
    """

    pending_documents = DocumentService.list_pending_documents(current_user)

    data = [
        {
            "doc_type": document_type.value
        }
        for document_type in pending_documents
    ]

    return jsonify(data), 200    


def get_document_by_id(current_user, document_id):

    fuso_sp = ZoneInfo("America/Sao_Paulo") 
    momento_requisicao = datetime.now(fuso_sp)

    #Endpoint GET /document/{document_id}

    # 1. Delega a busca e a validação de segurança para o Service
    document, error_reason = DocumentService.get_accessible_document(current_user, document_id)


    if error_reason == "NOT_FOUND":
        return jsonify({"error": "Documento não encontrado."}), 404


    if error_reason is not None:
 
        register_audit_log(current_user.id, LogAction.ACCESS_DENIED , "FAILURE", document_id,momento_requisicao, error_reason, selection_id_e=current_user.selection_id)
        
        print(f"[AUDIT LOG - ACCESS_DENIED]: {error_reason}")
        

        return jsonify({"error": "Acesso negado."}), 403
    

    storage = get_storage_service()

    url_visualizacao = storage.get_signed_url(document.storage_path, expiration_minutes=15)

    register_audit_log(current_user.id, LogAction.DOWNLOAD , "SUCCESS" , document_id, momento_requisicao, f"Link de download (URL assinada) gerado com sucesso para: {document.original_name}", selection_id_e=current_user.selection_id)

    return jsonify({
        "id": str(document.id),
        "original_name": document.original_name,
        "doc_type": document.type,
        # "file_size_kb": document.file_size_kb,
        "status": document.status,
        # "uploaded_by_name": str(document.uploaded_by) if hasattr(document, "uploader") else "Desconhecido",
        "selection_id": str(document.selection_id) if document.selection_id else None,
        "created_at": document.created_at.isoformat() + "Z" if document.created_at else None,
        "download_url": url_visualizacao
    }), 200




def download_document_url(current_user, document_id):
    
    fuso_sp = ZoneInfo("America/Sao_Paulo") 
    momento_requisicao = datetime.now(fuso_sp)

    # 1. Delega integralmente a busca e validação multi-tenant para o Service existente
    document, error_reason = DocumentService.get_accessible_document(current_user, document_id)

    if error_reason == "NOT_FOUND":
        return jsonify({"error": "Documento não encontrado."}), 404

    if error_reason is not None:
        # Registra a falha de segurança utilizando a função do projeto
        register_audit_log(current_user.id, LogAction.ACCESS_DENIED, "FAILURE", str(document_id), momento_requisicao, error_reason, selection_id_e=current_user.selection_id)
        return jsonify({"error": "Acesso negado."}), 403

    try:
        # 2. Consumo agnóstico do Storage Provider
        storage = get_storage_service()    # Chama a f  actory para decidir se é local ou cloud
        url_final = storage.get_signed_url(
            storage_path=document.storage_path,
            document_id=str(document.id),
            expiration_minutes=15
        )

        # 3. Registrar o sucesso do download na auditoria da FIFA
        
        register_audit_log(current_user.id, LogAction.DOWNLOAD, "SUCCESS", str(document.id), momento_requisicao, f"URL de download gerada para: {document.original_name}", selection_id_e=current_user.selection_id)
        return jsonify({
            "url": url_final,
            "expires_in_minutes": 15,
            "filename": document.original_name
        }), 200

    except NotFound as e:
        print(f"[ERRO STORAGE - BLOB NÃO ENCONTRADO]: {str(e)}")
        register_audit_log(current_user.id, LogAction.ACCESS_DENIED, "FAILURE", str(document_id), momento_requisicao, "Arquivo não encontrado no storage (removido ou corrompido).", selection_id_e=current_user.selection_id)
        return jsonify({"error": "Arquivo não encontrado no storage."}), 410

    except Exception as e:
        print(f"[ERRO STORAGE]: {str(e)}")
        register_audit_log(current_user.id, LogAction.ACCESS_DENIED, "FAILURE", str(document_id), momento_requisicao, "Serviço de armazenamento temporariamente indisponível.", selection_id_e=current_user.selection_id)
        return jsonify({"error": "Serviço de armazenamento temporariamente indisponível."}), 503
    



def stream_local_file(current_user, document_id):
    document, error_reason = DocumentService.get_accessible_document(current_user, document_id)

    if error_reason == "NOT_FOUND":
        return jsonify({"error": "Documento não encontrado."}), 404

    if error_reason is not None:
        return jsonify({"error": "Acesso negado."}), 403

    # 2. Critério de aceitação: verificar se o arquivo físico existe no disco rígido
    if not os.path.exists(document.storage_path):
        return jsonify({"error": "O arquivo físico não foi encontrado no servidor."}), 410

    # 3. Retorna o streaming de pedaços (chunks) nativo do Flask via send_file
    return send_file(
        document.storage_path,
        as_attachment=True,
        download_name=document.original_name
        )