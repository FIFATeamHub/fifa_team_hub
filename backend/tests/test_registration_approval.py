import uuid

from app.extensions import db
from app.models.enums.user_role import LogAction, RegistrationStatus, UserRole
from app.models.user import User
from app.services.auth import hash_password
from tests.conftest import get_latest_audit_log


def _criar_pendente(app, selection_id, email, full_name="Novato Pendente"):
    with app.app_context():
        user = User(
            full_name=full_name,
            email=email,
            password_hash=hash_password("123456"),
            role=UserRole.ATHELETE,
            registration_status=RegistrationStatus.PENDING,
            selection_id=selection_id,
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        db.session.expunge(user)
        return user


class TestListarPendentes:

    def test_auditor_ve_pendentes_da_propria_selecao(self, app, client, selection_bra, selection_arg, token_bra_auditor):
        pendente_bra = _criar_pendente(app, selection_bra, "pendente.bra@test.com")
        _criar_pendente(app, selection_arg, "pendente.arg@test.com")

        response = client.get(
            "/api/auth/registrations/pending",
            headers={"Authorization": f"Bearer {token_bra_auditor}"},
        )

        assert response.status_code == 200
        emails = [row["email"] for row in response.json["data"]]
        assert pendente_bra.email in emails
        assert "pendente.arg@test.com" not in emails

    def test_staff_tecnico_nao_pode_listar_pendentes(self, client, token_bra_staff):
        response = client.get(
            "/api/auth/registrations/pending",
            headers={"Authorization": f"Bearer {token_bra_staff}"},
        )

        assert response.status_code == 403
        assert "Acesso negado" in response.json["error"]

    def test_endpoint_exige_autenticacao(self, client):
        response = client.get("/api/auth/registrations/pending")

        assert response.status_code == 401


class TestAprovarCadastro:

    def test_auditor_aprova_cadastro_da_propria_selecao(self, app, client, db, selection_bra, token_bra_auditor):
        pendente = _criar_pendente(app, selection_bra, "aprovar.bra@test.com")

        response = client.post(
            f"/api/auth/registrations/{pendente.id}/approve",
            json={"role": "TECHNICAL_STAFF"},
            headers={"Authorization": f"Bearer {token_bra_auditor}"},
        )

        assert response.status_code == 200
        assert response.json["role"] == UserRole.TECHNICAL_STAFF.value
        assert response.json["registration_status"] == RegistrationStatus.APPROVED.value

        usuario_atualizado = db.get(User, pendente.id)
        assert usuario_atualizado.registration_status == RegistrationStatus.APPROVED
        assert usuario_atualizado.role == UserRole.TECHNICAL_STAFF

        audit_log = get_latest_audit_log(
            db, action=LogAction.REGISTER_APPROVED, status="SUCCESS"
        )
        assert audit_log is not None
        assert audit_log.resource_id == pendente.id

    def test_role_invalida_retorna_400(self, app, client, selection_bra, token_bra_auditor):
        pendente = _criar_pendente(app, selection_bra, "role.invalida@test.com")

        response = client.post(
            f"/api/auth/registrations/{pendente.id}/approve",
            json={"role": "SUPER_ADMIN"},
            headers={"Authorization": f"Bearer {token_bra_auditor}"},
        )

        assert response.status_code == 400

    def test_auditor_nao_pode_aprovar_cadastro_de_outra_selecao(self, app, client, selection_bra, selection_arg, token_bra_auditor):
        pendente_arg = _criar_pendente(app, selection_arg, "pendente.arg.aprovar@test.com")

        response = client.post(
            f"/api/auth/registrations/{pendente_arg.id}/approve",
            json={"role": "TECHNICAL_STAFF"},
            headers={"Authorization": f"Bearer {token_bra_auditor}"},
        )

        assert response.status_code == 403

    def test_staff_tecnico_nao_pode_aprovar(self, app, selection_bra, client, token_bra_staff):
        pendente = _criar_pendente(app, selection_bra, "sem.permissao@test.com")

        response = client.post(
            f"/api/auth/registrations/{pendente.id}/approve",
            json={"role": "TECHNICAL_STAFF"},
            headers={"Authorization": f"Bearer {token_bra_staff}"},
        )

        assert response.status_code == 403

    def test_usuario_inexistente_retorna_404(self, client, token_bra_auditor):
        response = client.post(
            f"/api/auth/registrations/{uuid.uuid4()}/approve",
            json={"role": "TECHNICAL_STAFF"},
            headers={"Authorization": f"Bearer {token_bra_auditor}"},
        )

        assert response.status_code == 404

    def test_cadastro_ja_processado_retorna_409(self, app, client, selection_bra, token_bra_auditor):
        pendente = _criar_pendente(app, selection_bra, "duas.vezes@test.com")

        client.post(
            f"/api/auth/registrations/{pendente.id}/approve",
            json={"role": "TECHNICAL_STAFF"},
            headers={"Authorization": f"Bearer {token_bra_auditor}"},
        )

        response = client.post(
            f"/api/auth/registrations/{pendente.id}/approve",
            json={"role": "TECHNICAL_STAFF"},
            headers={"Authorization": f"Bearer {token_bra_auditor}"},
        )

        assert response.status_code == 409


class TestRejeitarCadastro:

    def test_auditor_rejeita_cadastro_da_propria_selecao(self, app, client, db, selection_bra, token_bra_auditor):
        pendente = _criar_pendente(app, selection_bra, "rejeitar.bra@test.com")

        response = client.post(
            f"/api/auth/registrations/{pendente.id}/reject",
            headers={"Authorization": f"Bearer {token_bra_auditor}"},
        )

        assert response.status_code == 200
        assert response.json["registration_status"] == RegistrationStatus.REJECTED.value

        usuario_atualizado = db.get(User, pendente.id)
        assert usuario_atualizado.registration_status == RegistrationStatus.REJECTED

        audit_log = get_latest_audit_log(
            db, action=LogAction.REGISTER_REJECTED, status="SUCCESS"
        )
        assert audit_log is not None
        assert audit_log.resource_id == pendente.id

    def test_auditor_nao_pode_rejeitar_cadastro_de_outra_selecao(self, app, client, selection_bra, selection_arg, token_bra_auditor):
        pendente_arg = _criar_pendente(app, selection_arg, "pendente.arg.rejeitar@test.com")

        response = client.post(
            f"/api/auth/registrations/{pendente_arg.id}/reject",
            headers={"Authorization": f"Bearer {token_bra_auditor}"},
        )

        assert response.status_code == 403

    def test_staff_tecnico_nao_pode_rejeitar(self, app, selection_bra, client, token_bra_staff):
        pendente = _criar_pendente(app, selection_bra, "sem.permissao.rejeitar@test.com")

        response = client.post(
            f"/api/auth/registrations/{pendente.id}/reject",
            headers={"Authorization": f"Bearer {token_bra_staff}"},
        )

        assert response.status_code == 403
