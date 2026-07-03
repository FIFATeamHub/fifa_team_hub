import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from jose import jwt, JWTError
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))

def hash_senha(senha: str) -> str:
    return generate_password_hash(senha)

def verificar_senha(senha: str, hash: str) -> bool:
    return check_password_hash(hash, senha)

def gerar_token(user) -> str:
    payload = {
        "sub": str(user.id),
        "role": user.role.value,
        "selection_id": str(user.selection_id) if user.selection_id else None,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

def decodificar_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None

def verify_password(plain_pass, hashed_pass):
    return check_password_hash(hashed_pass, plain_pass)

def create_access_token(data):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm="HS256")

def decode_token(token):
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])