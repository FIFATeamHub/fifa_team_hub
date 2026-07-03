from uuid import uuid4

from app.models.user import User
from app.models.enums.user_role import UserRole
from werkzeug.security import generate_password_hash
from app.services.auth import verify_password, create_access_token, decode_token

class MockUser:
    def __init__(self, password):
        self.password_hash = generate_password_hash(password)


def test_user_password_hash_not_plaintext():
    password = "senha123"
    user = MockUser(password)

    assert user.password_hash != password


def test_verify_password():

    password = "senha123"
    hashed = generate_password_hash(password)

    assert verify_password(password, hashed)
    assert not verify_password("senha_errada", hashed)


def test_create_and_decode_token():

    user = User(
        id=uuid4(),
        role=UserRole.ORGANIZER,
        selection_id=uuid4()
    )

    token = create_access_token(user)

    decoded = decode_token(token)

    assert decoded["sub"] == str(user.id)
    assert decoded["role"] == UserRole.ORGANIZER.value
    assert decoded["selection_id"] == str(user.selection_id)
    assert "exp" in decoded