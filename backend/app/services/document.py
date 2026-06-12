import magic
from flask import jsonify


ALLOWED_MIME_TYPES = {
    "application/pdf", 
    "image/jpeg", 
    "image/png",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document" # .docx
}

MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

def validar_arquivo_seguranca(arquivo_fisico):

    #Retorna (True, None) se estiver limpo, ou (False, dicionário_de_erro) se violar regras.
   
    
    # 1. Validação de Tamanho (Evita sobrecarga do servidor)

    arquivo_fisico.seek(0, 2)
    tamanho_bytes = arquivo_fisico.tell()

  
    arquivo_fisico.seek(0)

    if tamanho_bytes > MAX_SIZE_BYTES:
        return False, {"error": "Arquivo muito grande. O limite máximo é 10 MB", "status_code": 413}

    # 2. Validação Real de Natureza (MIME Type) via python-magic

    primeiros_bytes = arquivo_fisico.read(2048)
    arquivo_fisico.seek(0) # Reseta o cursor de leitura de novo

    mime_tipo_real = magic.from_buffer(primeiros_bytes, mime=True)

    if mime_tipo_real not in ALLOWED_MIME_TYPES:
        return False, {
            "error": f"Tipo de mídia '{mime_tipo_real}' não permitido. Envie PDF, JPEG ou PNG.", 
            "status_code": 415
        }


    return True, {"file_size_kb": int(tamanho_bytes / 1024), "mime_type": mime_tipo_real}