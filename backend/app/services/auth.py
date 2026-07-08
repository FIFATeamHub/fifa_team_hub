import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import jwt
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return check_password_hash(hashed_password, plain_password)


def user_to_token_payload(user) -> dict:
    return {
        "sub": str(user.id),
        "role": user.role.value,
        "selection_id": (
            str(user.selection_id)
            if user.selection_id is not None
            else None
        ),
    }


def create_access_token(data) -> str:

    if isinstance(data, dict):
        payload = data.copy()
    else:
        payload = user_to_token_payload(data)

    payload["exp"] = (
        datetime.now(timezone.utc)
        + timedelta(minutes=JWT_EXPIRE_MINUTES)
    )

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm="HS256"
    )


def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=["HS256"],
    )

