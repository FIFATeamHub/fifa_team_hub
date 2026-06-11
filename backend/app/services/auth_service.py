import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
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
        "sub": str(user.id),
        "role": user.role.value,
        "selection_id": str(user.selection_id) if user.selection_id else None,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")


def decodificar_token(token: str):
    # Retorna o payload se válido, None se inválido/expirado
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None