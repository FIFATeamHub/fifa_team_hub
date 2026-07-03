import pytest
from werkzeug.security import generate_password_hash
from app.services.auth import verify_password, create_access_token, decode_token

class MockUser:
    def __init__(self, password):
        self.password_hash = generate_password_hash(password)

def test_user_password_hash_not_plaintext():
    plain_password = "senha_de_teste_123"
    user = MockUser(plain_password)
    
    assert user.password_hash != plain_password

def test_verify_password():
    plain_password = "outra_senha_segura"
    hashed_password = generate_password_hash(plain_password)
    
    assert verify_password(plain_password, hashed_password) is True
    assert verify_password("senha_totalmente_errada", hashed_password) is False

def test_create_and_decode_token():
    data = {"user_id": 99, "role": "admin", "selection_id": 5}
    
    token = create_access_token(data)
    decoded_data = decode_token(token)
    
    assert decoded_data["user_id"] == data["user_id"]
    assert decoded_data["role"] == data["role"]
    assert decoded_data["selection_id"] == data["selection_id"]
    assert "exp" in decoded_data