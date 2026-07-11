from app.models.enums.user_role import LogAction
from tests.conftest import get_latest_audit_log


class TestLogout:
    """Cobre o endpoint de logout e o registro de log de auditoria (AuditLog)."""

    def test_logout_sem_token_retorna_401(self, client):
        response = client.post("/auth/logout")

        assert response.status_code == 401

    def test_logout_sucesso_registra_audit_log(self, client, db, bra_staff, token_bra_staff):
        response = client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {token_bra_staff}"},
        )

        assert response.status_code == 200

        audit_log = get_latest_audit_log(
            db, action=LogAction.LOGOUT, user_id=bra_staff.id, status="SUCCESS"
        )
        assert audit_log is not None
        assert audit_log.resource_id == bra_staff.id
        assert audit_log.ip_address is not None


class TestLoginAuditLog:
    """Cobre o registro de log de auditoria (AuditLog) no endpoint de login."""

    def test_login_sucesso_registra_audit_log(self, client, db, bra_staff):
        response = client.post(
            "/auth/login",
            json={"email": bra_staff.email, "password": "123456"},
        )

        assert response.status_code == 200
        assert "access_token" in response.json

        audit_log = get_latest_audit_log(
            db, action=LogAction.LOGIN, user_id=bra_staff.id, status="SUCCESS"
        )
        assert audit_log is not None
        assert audit_log.resource_id == bra_staff.id
        assert audit_log.ip_address is not None
        assert "sucesso" in audit_log.details.lower()
        assert "123456" not in audit_log.details

    def test_login_senha_incorreta_registra_audit_log_com_user_id(self, client, db, bra_staff):
        response = client.post(
            "/auth/login",
            json={"email": bra_staff.email, "password": "senha-errada"},
        )

        assert response.status_code == 401
        assert response.json["error"] == "Credenciais inválidas"

        audit_log = get_latest_audit_log(
            db, action=LogAction.LOGIN, user_id=bra_staff.id, status="FAILED"
        )
        assert audit_log is not None
        assert audit_log.ip_address is not None
        assert "senha-errada" not in audit_log.details

    def test_login_usuario_inexistente_registra_audit_log_sem_user_id(self, client, db):
        response = client.post(
            "/auth/login",
            json={"email": "nao.existe@test.com", "password": "qualquer-coisa"},
        )

        assert response.status_code == 401
        assert response.json["error"] == "Credenciais inválidas"

        audit_log = get_latest_audit_log(
            db, action=LogAction.LOGIN, status="FAILED"
        )
        assert audit_log is not None
        assert audit_log.user_id is None
        assert "não cadastrado" in audit_log.details.lower() or "não encontrado" in audit_log.details.lower()
        assert "qualquer-coisa" not in audit_log.details
