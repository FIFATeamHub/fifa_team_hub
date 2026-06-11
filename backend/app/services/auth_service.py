import os
from dotenv import load_dotenv

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
from jose import jwt

load_dotenv() #Lê o arquivo .env, que vai ser utilizado mais tarde

def hash_password(plain_pass):
    return generate_password_hash(plain_pass)

def verify_password(plain_pass, hashed_pass):
    return check_password_hash(hashed_pass, plain_pass)

def create_access_token(data):
    to_encode = data.copy()

    expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes) #Define quando expira o token
    
    to_encode.update({"exp": expire})

    secret_key = os.getenv("JWT_SECRET_KEY")
    return jwt.encode(to_encode, secret_key, algorithm="HS256") #Gera o JWT (header.payload.assinatura)

def decode_token(token):
    secret_key = os.getenv("JWT_SECRET_KEY")
    return jwt.decode(token, secret_key, algorithms=["HS256"])
