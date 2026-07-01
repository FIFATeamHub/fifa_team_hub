import pytest


def test_sem_token(client):

    response = client.get("/auth/me")

    assert response.status_code == 401


def test_header_invalido(client):

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "abc"
        }
    )

    assert response.status_code == 401


def test_token_invalido(client):

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer token-invalido"
        }
    )

    assert response.status_code == 401


def test_token_valido(client, token_organizer):

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token_organizer}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["email"] == "organizer@test.com"
    assert data["role"] == "ORGANIZER"