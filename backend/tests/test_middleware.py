from unittest.mock import patch
from jose import JWTError, ExpiredSignatureError

# Payload para um token válido - sem precisar de um banco
PAYLOAD_VALIDO = {
    "sub": "uuid-fake-123",
    "role": "ORGANIZER",
    "selection_id": None
}

def test_sem_token_retornar_401(client):
    response = client.get("/test/protegida")
    assert response.status_code == 401
    assert "Token não fornecido" in response.get_json()["error"]

def test_header_malformado_retorna_401(client):
    response = client.get("/test/protegida", headers={"Authorization": "tokensembearer"})
    assert response.status_code == 401

def test_token_expirado_retorna_401(client):
    with patch("app.middlewares.auth.decodificar_token") as mock:
        mock.side_effect = ExpiredSignatureError()
        response = client.get("/test/protegida", headers={"Authorization": "Bearer qualquer"})
    assert response.status_code == 401
    assert "expirado" in response.get_json()["error"]

def test_token_invalido_retorna_401(client):
    with patch("app.middlewares.auth.decodificar_token") as mock:
        mock.side_effect = JWTError()
        response = client.get("/test/protegida", headers={"Authorization": "Bearer invalido"})
    assert response.status_code == 401
    assert "inválido" in response.get_json()["error"]

def test_token_valido_retorna_200(client):
    """
    Valida se o token é aceito e se g.current_user_role 
    e g.current_selection_id estão disponíveis na rota
    """
    with patch("app.middlewares.auth.decodificar_token") as mock:
        mock.return_value = PAYLOAD_VALIDO
        response = client.get("/test/protegida", headers={"Authorization": "Bearer valido"})
    
    assert response.status_code == 200
    
    # PEGA O JSON PARA VALIDAR O REQUISITO DOS DADOS DISPONÍVEIS NO 'g'
    dados_resposta = response.get_json()
    assert dados_resposta["user_id"] == "uuid-fake-123"
    assert dados_resposta["role"] == "ORGANIZER"      # Valida g.current_user_role
    assert dados_resposta["selection_id"] is None     # Valida g.current_selection_id

def test_role_errada_retorna_403(client):
    """
    Valida que o decorator de role barra usuários não autorizados (403)
    """
    # Usuário com role diferente (ATHLETE) tentando acessar rota de ORGANIZER
    payload_atleta = {**PAYLOAD_VALIDO, "role": "ATHLETE"} 
    
    with patch("app.middlewares.auth.decodificar_token") as mock:
        mock.return_value = payload_atleta
        response = client.get("/test/so-organizer", headers={"Authorization": "Bearer valido"})
        
    assert response.status_code == 403