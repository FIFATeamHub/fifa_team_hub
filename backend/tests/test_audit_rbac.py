def test_auditor_pode_acessar_logs(client, token_auditor):
    response = client.get(
        "/api/audit/", 
        headers={"Authorization": f"Bearer {token_auditor}"}
    )
    assert response.status_code == 200
    assert "data" in response.json
    assert "pagination" in response.json

def test_staff_tecnico_nao_pode_acessar_logs(client, token_bra_staff):
    response = client.get(
        "/api/audit/", 
        headers={"Authorization": f"Bearer {token_bra_staff}"}
    )
    assert response.status_code == 403
    assert "Acesso negado" in response.json["error"]
