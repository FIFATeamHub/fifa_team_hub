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


class TestAprovacaoDeAuditor:

    def test_organizer_aprova_auditor(self, app, client, db, selection_bra, organizer, token_organizer):
        pendente = _criar_pendente(app, selection_bra, "novo.auditor@test.com")

        response = client.post(
            f"/api/auth/registrations/{pendente.id}/approve",
            json={"role": "AUDITOR"},
            headers={"Authorization": f"Bearer {token_organizer}"},
        )

        assert response.status_code == 200
        assert response.json["role"] == UserRole.AUDITOR.value
        assert response.json["registration_status"] == RegistrationStatus.APPROVED.value

        usuario_atualizado = db.get(User, pendente.id)
        assert usuario_atualizado.role == UserRole.AUDITOR
        assert usuario_atualizado.registration_status == RegistrationStatus.APPROVED

        audit_log = get_latest_audit_log(
            db, action=LogAction.REGISTER_APPROVED, status="SUCCESS"
        )
        assert audit_log is not None
        assert audit_log.resource_id == pendente.id
        assert audit_log.user_id == organizer.id
        assert str(organizer.id) in audit_log.details
        assert "AUDITOR" in audit_log.details

    def test_auditor_escalona_nomeacao_de_auditor(self, app, client, db, selection_bra, bra_auditor, token_bra_auditor):
        pendente = _criar_pendente(app, selection_bra, "auditor.nomeado@test.com")

        response = client.post(
            f"/api/auth/registrations/{pendente.id}/approve",
            json={"role": "AUDITOR"},
            headers={"Authorization": f"Bearer {token_bra_auditor}"},
        )

        assert response.status_code == 202
        assert response.json["message"] == "Solicitação de cadastro de auditor enviada para aprovação do Organizador"

        usuario_ainda_pendente = db.get(User, pendente.id)
        assert usuario_ainda_pendente.registration_status == RegistrationStatus.PENDING
        assert usuario_ainda_pendente.role == UserRole.ATHELETE

        audit_log = get_latest_audit_log(
            db, action=LogAction.AUDITOR_NOMINATION_REQUESTED, status="SUCCESS"
        )
        assert audit_log is not None
        assert audit_log.resource_id == pendente.id
        assert audit_log.user_id == bra_auditor.id

    def test_staff_nao_pode_escalonar_nomeacao_de_auditor(self, app, client, selection_bra, token_bra_staff):
        pendente = _criar_pendente(app, selection_bra, "auditor.negado@test.com")

        response = client.post(
            f"/api/auth/registrations/{pendente.id}/approve",
            json={"role": "AUDITOR"},
            headers={"Authorization": f"Bearer {token_bra_staff}"},
        )

        assert response.status_code == 403
        assert response.json["error"] == "Apenas Organizadores podem aprovar Auditores"

    def test_auditor_aprova_athlete_e_staff_da_propria_selecao(self, app, client, db, selection_bra, token_bra_auditor):
        pendente_atleta = _criar_pendente(app, selection_bra, "atleta.aprovado@test.com")
        pendente_staff = _criar_pendente(app, selection_bra, "staff.aprovado@test.com")

        response_atleta = client.post(
            f"/api/auth/registrations/{pendente_atleta.id}/approve",
            json={"role": "ATHELETE"},
            headers={"Authorization": f"Bearer {token_bra_auditor}"},
        )
        response_staff = client.post(
            f"/api/auth/registrations/{pendente_staff.id}/approve",
            json={"role": "TECHNICAL_STAFF"},
            headers={"Authorization": f"Bearer {token_bra_auditor}"},
        )

        assert response_atleta.status_code == 200
        assert response_atleta.json["role"] == UserRole.ATHELETE.value

        assert response_staff.status_code == 200
        assert response_staff.json["role"] == UserRole.TECHNICAL_STAFF.value

        assert db.get(User, pendente_atleta.id).registration_status == RegistrationStatus.APPROVED
        assert db.get(User, pendente_staff.id).registration_status == RegistrationStatus.APPROVED


class TestListagemNomeacoesAuditor:

    def test_organizer_ve_apenas_nomeados_para_auditor(
        self, app, client, selection_bra, selection_arg, token_bra_auditor, token_organizer
    ):
        nomeado = _criar_pendente(app, selection_bra, "nomeado.auditor@test.com")
        comum = _criar_pendente(app, selection_bra, "comum.pendente@test.com")
        _criar_pendente(app, selection_arg, "outro.pendente@test.com")

        escalonado_pelo_auditor = client.post(
            f"/api/auth/registrations/{nomeado.id}/approve",
            json={"role": "AUDITOR"},
            headers={"Authorization": f"Bearer {token_bra_auditor}"},
        )
        assert escalonado_pelo_auditor.status_code == 202

        response = client.get(
            "/api/auth/registrations/pending",
            headers={"Authorization": f"Bearer {token_organizer}"},
        )

        assert response.status_code == 200
        emails = [row["email"] for row in response.json["data"]]
        assert nomeado.email in emails
        assert comum.email not in emails
        assert "outro.pendente@test.com" not in emails

    def test_organizer_nao_pode_listar_sem_role_organizer_ou_auditor(self, client, token_bra_staff):
        response = client.get(
            "/api/auth/registrations/pending",
            headers={"Authorization": f"Bearer {token_bra_staff}"},
        )

        assert response.status_code == 403
        assert "Acesso negado" in response.json["error"]
