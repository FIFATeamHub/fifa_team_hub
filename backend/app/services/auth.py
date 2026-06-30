import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
from werkzeug.security import generate_password_hash, check_password_hash

# Lê do .env — nunca hardcoded
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))


def hash_senha(senha: str) -> str:
    # werkzeug para gerar o hash da senha
    return generate_password_hash(senha)


def verificar_senha(senha: str, hash: str) -> bool:
    # werkzeug para verificar a senha contra o hash
    return check_password_hash(hash, senha)


def gerar_token(user) -> str:
    # Monta o payload com dados essenciais do usuário
    payload = {
        "sub": str(user.id), #id do user
        "role": user.role.value, #auditor, admin ...
        "selection_id": str(user.selection_id) if user.selection_id else None, #seleção que está vinculada
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES) #tempo de inspiração do token
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")


def decodificar_token(token: str) -> dict:
    # Lança exceção — deixa o middleware decidir a resposta HTTP
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError:
        raise #token expirado

    except JWTError:
        raise #token invalido