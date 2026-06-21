import os
from dotenv import load_dotenv

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
from jose import jwt

load_dotenv() #Lê o arquivo .env, que vai ser utilizado mais tarde

def verify_password(plain_pass, hashed_pass):
    return check_password_hash(hashed_pass, plain_pass)

def create_access_token(data):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=os.getenv("JWT_EXPIRE_MINUTES")) #Define quando expira o token
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, os.getenv().JWT_SECRET_KEY, algorithm="HS256") #Gera o JWT (header.payload.assinatura)

def decode_token(token):
    return jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=["HS256"])