import magic
from flask import jsonify
from app.models.enums.user_role import TypeDocument, DocStatus
from app.models.enums.user_role import UserRole


ALLOWED_MIME_TYPES = {
    "application/pdf", 
    "image/jpeg", 
    "image/png",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}

MAX_SIZE_BYTES = 10 * 1024 * 1024 

def validate_file(arquivo_fisico):   
    
    # 1. Validação de Tamanho

    arquivo_fisico.seek(0, 2)
    tamanho_bytes = arquivo_fisico.tell()

  
    arquivo_fisico.seek(0)

    if tamanho_bytes > MAX_SIZE_BYTES:
        return False, {"error": "Arquivo muito grande. O limite máximo é 10 MB", "status_code": 413}

    # 2. Validação Real de Natureza (MIME Type) via python-magic

    primeiros_bytes = arquivo_fisico.read(2048)
    arquivo_fisico.seek(0)

    mime_tipo_real = magic.from_buffer(primeiros_bytes, mime=True)

    if mime_tipo_real not in ALLOWED_MIME_TYPES:
        return False, {
            "error": f"Tipo de mídia '{mime_tipo_real}' não permitido. Envie PDF, JPEG ou PNG.", 
            "status_code": 415
        }


    return True, {"file_size_kb": int(tamanho_bytes / 1024), "mime_type": mime_tipo_real}





def validate_upload_permission(user_role, doc_type_enum):

    if user_role == UserRole.AUDITOR:
        if doc_type_enum == TypeDocument.PASSPORT:
            return True, DocStatus.PENDING.value


    elif user_role == UserRole.TECHNICAL_STAFF:
        if doc_type_enum.name in ["CONVOCADO", "RELATORIO_TATICO", "ESQUEMA_JOGADAS"]:
            return True, DocStatus.APPROVED.value

        if doc_type_enum.name in ["PASSPORT", "LAUDO_MEDICO"]:
            return True, DocStatus.PENDING.value


    elif user_role == UserRole.MEDICAL_STAFF:
        if doc_type_enum.name in ["LAUDO_MEDICO"]:
            return True, DocStatus.PENDING.value
        
        if doc_type_enum == TypeDocument.PASSPORT:
            return True, DocStatus.PENDING.value

    elif user_role == UserRole.ATHELETE:
        if doc_type_enum.name in ["PASSPORT", "LAUDO_MEDICO"]:
            return True, DocStatus.PENDING.value

    # Qualquer outra combinação não permitida
    return False, None