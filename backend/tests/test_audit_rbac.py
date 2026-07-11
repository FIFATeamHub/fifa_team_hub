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


def test_auditor_nao_ve_logs_de_outra_selecao(app, client, db, selection_bra, selection_arg, token_bra_auditor):
    import uuid
    from app.models.audit_log import AuditLog
    from app.models.enums.user_role import LogAction

    with app.app_context():
        db.add(AuditLog(
            user_id=None,
            action=LogAction.LOGIN,
            resource_id=uuid.uuid4(),
            ip_address="127.0.0.1",
            status="SUCCESS",
            details="login selecao bra",
            selection_id=selection_bra,
        ))
        db.add(AuditLog(
            user_id=None,
            action=LogAction.LOGIN,
            resource_id=uuid.uuid4(),
            ip_address="127.0.0.1",
            status="SUCCESS",
            details="login selecao arg",
            selection_id=selection_arg,
        ))
        db.commit()

    response = client.get(
        "/api/audit/",
        headers={"Authorization": f"Bearer {token_bra_auditor}"}
    )

    assert response.status_code == 200
    details = [row["details"] for row in response.json["data"]]
    assert "login selecao bra" in details
    assert "login selecao arg" not in details
