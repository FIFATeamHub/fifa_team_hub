from flask import jsonify, request
from app.services.document_get import DocumentService
from app.models.enums.user_role import  LogAction
from app.controllers.document_upload import register_audit_log
from datetime import datetime, timezone
from zoneinfo import ZoneInfo



def list_documents(current_user): 
    doc_type_filter = request.args.get("type")
    
    # Captura a paginação tratando como inteiro e definindo os fallbacks padrão (1 e 10)
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
        register_audit_log(current_user.id, LogAction.ACCESS_DENIED , "FAILURE", "00000000-0000-0000-0000-000000000000" ,momento_requisicao, "Acesso negado. Perfil inválido.")
        return jsonify({"error": "Acesso negado. Perfil inválido."}), 403

    # 3. FORMATAÇÃO DO JSON DE RETORNO (Higienização de dados)
    # Transforma os objetos do banco em dicionários puros sem vazar o 'storage_path'
    data_list = []
    for doc in paginated_result.items:
        data_list.append({
            "id": str(doc.id),
            "original_name": doc.original_name,   #Mudado de doc.original_name para doc.filename
            "doc_type": doc.type.value if hasattr(doc.type, "value") else str(doc.type), # Trata o Enum de forma segura
            "storage_url": doc.storage_url, # Adicionado conforme o Model
            "status": doc.status,
            "uploaded_by_id": str(doc.uploaded_by), # Mapeado diretamente do relacionamento/FK do Model
            "selection_id": str(doc.selection_id) if doc.selection_id else None,
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


def get_document_by_id(current_user, document_id):

    fuso_sp = ZoneInfo("America/Sao_Paulo") 
    momento_requisicao = datetime.now(fuso_sp)

    # 1. Delega a busca e a validação de segurança para o Service
    document, error_reason = DocumentService.get_accessible_document(current_user, document_id)

    # 2. Tratamento de Erro - Documento não encontrado no Banco (404)
    if error_reason == "NOT_FOUND":
        return jsonify({"error": "Documento não encontrado."}), 404

    # 3. Tratamento de Erro - Bloqueio de Segurança / Invasão (403)
    if error_reason is not None:
        # REGISTRO NO AUDIT LOG (Obrigatório pela US-012)
        # Se você tiver a função, você a executa passando o motivo real (error_reason) no campo 'details'
        register_audit_log(current_user.id, LogAction.ACCESS_DENIED , "FAILURE", document_id,momento_requisicao, error_reason)
        
        print(f"[AUDIT LOG - ACCESS_DENIED]: {error_reason}") # Apenas ilustrativo por enquanto
        
        # Para o usuário externo, retornamos uma mensagem padrão discreta por segurança
        return jsonify({"error": "Acesso negado."}), 403

    # 4. Sucesso: Higienização e Entrega dos Metadados (Sem vazar o storage_path)
    return jsonify({
        "id": str(document.id),
        "original_name": document.original_name,
        "doc_type": document.type,
        # "file_size_kb": document.file_size_kb,
        "status": document.status,
        # "uploaded_by_name": str(document.uploaded_by) if hasattr(document, "uploader") else "Desconhecido",
        "selection_id": str(document.selection_id) if document.selection_id else None,
        "created_at": document.created_at.isoformat() + "Z" if document.created_at else None
    }), 200