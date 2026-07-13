import uuid

from app.models.enums.user_role import LogAction, RegistrationStatus, UserRole
from app.models.user import User
from app.services.auth import hash_password
from app.extensions import db
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
            db, action=LogAction.LOGIN, user_id=bra_staff.id, status="FAILURE"
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
            db, action=LogAction.LOGIN, status="FAILURE"
        )
        assert audit_log is not None
        assert audit_log.user_id is None
        assert "não cadastrado" in audit_log.details.lower() or "não encontrado" in audit_log.details.lower()
        assert "qualquer-coisa" not in audit_log.details


class TestRegisterRoleInjection:

    def test_payload_malicioso_com_role_auditor_e_rejeitado(self, client, db, selection_bra):
        response = client.post(
            "/auth/register",
            json={
                "email": "usuario.malicioso@test.com",
                "password": "senha1234",
                "full_name": "Usuario Malicioso",
                "selection_id": str(selection_bra),
                "role": "AUDITOR",
            },
        )

        assert response.status_code == 400

        usuario_criado = User.query.filter_by(email="usuario.malicioso@test.com").first()
        assert usuario_criado is None

    def test_cadastro_sem_role_continua_funcionando(self, client, selection_bra):
        response = client.post(
            "/auth/register",
            json={
                "email": "usuario.legitimo@test.com",
                "password": "senha1234",
                "full_name": "Usuario Legitimo",
                "selection_id": str(selection_bra),
            },
        )

        assert response.status_code == 201
        assert response.json["role"] == UserRole.ATHELETE.value

    def test_selection_id_e_obrigatorio(self, client):
        response = client.post(
            "/auth/register",
            json={
                "email": "sem.selecao@test.com",
                "password": "senha1234",
                "full_name": "Sem Selecao",
            },
        )

        assert response.status_code == 400

    def test_selection_id_inexistente_retorna_400(self, client):
        response = client.post(
            "/auth/register",
            json={
                "email": "selecao.invalida@test.com",
                "password": "senha1234",
                "full_name": "Selecao Invalida",
                "selection_id": str(uuid.uuid4()),
            },
        )

        assert response.status_code == 400

    def test_payload_malicioso_com_registration_status_e_rejeitado(self, client, db, selection_bra):
        response = client.post(
            "/auth/register",
            json={
                "email": "novato.malicioso@test.com",
                "password": "senha1234",
                "full_name": "Novato Malicioso",
                "selection_id": str(selection_bra),
                "registration_status": "APPROVED",
            },
        )

        assert response.status_code == 400

        usuario_criado = User.query.filter_by(email="novato.malicioso@test.com").first()
        assert usuario_criado is None

    def test_cadastro_e_sempre_criado_como_pending(self, client, db, selection_bra):
        response = client.post(
            "/auth/register",
            json={
                "email": "novato@test.com",
                "password": "senha1234",
                "full_name": "Novato",
                "selection_id": str(selection_bra),
            },
        )

        assert response.status_code == 201

        usuario_criado = User.query.filter_by(email="novato@test.com").first()
        assert usuario_criado.registration_status == RegistrationStatus.PENDING


class TestLoginRegistrationStatus:
    """Cobre o bloqueio de login para cadastros não aprovados."""

    def _criar_usuario(self, app, selection_bra, status, email):
        with app.app_context():
            user = User(
                full_name="Usuario Teste",
                email=email,
                password_hash=hash_password("123456"),
                role=UserRole.ATHELETE,
                registration_status=status,
                selection_id=selection_bra,
            )
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)
            db.session.expunge(user)
            return user

    def test_login_pending_retorna_403_e_nao_gera_token(self, app, client, db, selection_bra):
        user = self._criar_usuario(
            app, selection_bra, RegistrationStatus.PENDING, "pendente@test.com"
        )

        response = client.post(
            "/auth/login",
            json={"email": user.email, "password": "123456"},
        )

        assert response.status_code == 403
        assert response.json["error"] == "Cadastro pendente de aprovação do Auditor"
        assert "access_token" not in response.json

        audit_log = get_latest_audit_log(
            db, action=LogAction.ACCESS_DENIED, user_id=user.id, status="FAILURE"
        )
        assert audit_log is not None

    def test_login_rejected_retorna_403_e_nao_gera_token(self, app, client, db, selection_bra):
        user = self._criar_usuario(
            app, selection_bra, RegistrationStatus.REJECTED, "rejeitado@test.com"
        )

        response = client.post(
            "/auth/login",
            json={"email": user.email, "password": "123456"},
        )

        assert response.status_code == 403
        assert response.json["error"] == "Cadastro rejeitado pelo Auditor"
        assert "access_token" not in response.json

        audit_log = get_latest_audit_log(
            db, action=LogAction.ACCESS_DENIED, user_id=user.id, status="FAILURE"
        )
        assert audit_log is not None

    def test_login_approved_retorna_200_e_gera_token(self, app, client, db, selection_bra):
        user = self._criar_usuario(
            app, selection_bra, RegistrationStatus.APPROVED, "aprovado@test.com"
        )

        response = client.post(
            "/auth/login",
            json={"email": user.email, "password": "123456"},
        )

        assert response.status_code == 200
        assert "access_token" in response.json
