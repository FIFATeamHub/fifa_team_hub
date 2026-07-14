from app.models.enums.user_role import RegistrationStatus, UserRole
from app.models.selection import Selection
from app.models.user import User


def _payload(**overrides):
    dados = {
        "name": "France",
        "code": "FRA",
        "auditor_name": "Auditor França",
        "auditor_email": "auditor.fra@test.com",
        "auditor_password": "senha1234",
    }
    dados.update(overrides)
    return dados


class TestRBACCriacaoDeSelection:

    def test_organizer_cria_selecao_e_auditor(self, app, client, db, token_organizer):
        response = client.post(
            "/api/selection/",
            json=_payload(),
            headers={"Authorization": f"Bearer {token_organizer}"},
        )

        assert response.status_code == 201
        assert response.json["selection"]["code"] == "FRA"
        assert response.json["auditor"]["role"] == UserRole.AUDITOR.value

        with app.app_context():
            selecao = Selection.query.filter_by(code="FRA").first()
            assert selecao is not None

            auditor = User.query.filter_by(email="auditor.fra@test.com").first()
            assert auditor is not None
            assert auditor.role == UserRole.AUDITOR
            assert auditor.registration_status == RegistrationStatus.APPROVED
            assert auditor.selection_id == selecao.id

    def test_auditor_nao_pode_criar_selecao(self, client, token_auditor):
        response = client.post(
            "/api/selection/",
            json=_payload(),
            headers={"Authorization": f"Bearer {token_auditor}"},
        )

        assert response.status_code == 403
        assert "Acesso negado" in response.json["error"]

    def test_staff_nao_pode_criar_selecao(self, client, token_bra_staff):
        response = client.post(
            "/api/selection/",
            json=_payload(),
            headers={"Authorization": f"Bearer {token_bra_staff}"},
        )

        assert response.status_code == 403
        assert "Acesso negado" in response.json["error"]

    def test_athlete_nao_pode_criar_selecao(self, client, token_bra_athlete):
        response = client.post(
            "/api/selection/",
            json=_payload(),
            headers={"Authorization": f"Bearer {token_bra_athlete}"},
        )

        assert response.status_code == 403
        assert "Acesso negado" in response.json["error"]

    def test_requer_autenticacao(self, client):
        response = client.post("/api/selection/", json=_payload())

        assert response.status_code == 401


class TestValidacaoDePayload:

    def test_campo_obrigatorio_ausente(self, client, token_organizer):
        dados = _payload()
        del dados["auditor_password"]

        response = client.post(
            "/api/selection/",
            json=dados,
            headers={"Authorization": f"Bearer {token_organizer}"},
        )

        assert response.status_code == 400
        assert "auditor_password" in response.json["error"]

    def test_codigo_deve_ter_3_caracteres(self, client, token_organizer):
        response = client.post(
            "/api/selection/",
            json=_payload(code="FRAN"),
            headers={"Authorization": f"Bearer {token_organizer}"},
        )

        assert response.status_code == 400

    def test_senha_curta_e_rejeitada(self, client, token_organizer):
        response = client.post(
            "/api/selection/",
            json=_payload(auditor_password="123"),
            headers={"Authorization": f"Bearer {token_organizer}"},
        )

        assert response.status_code == 400

    def test_codigo_duplicado_retorna_400(self, app, client, db, selection_bra, token_organizer):
        response = client.post(
            "/api/selection/",
            json=_payload(code="BRA", auditor_email="outro.auditor@test.com"),
            headers={"Authorization": f"Bearer {token_organizer}"},
        )

        assert response.status_code == 400
        assert "código" in response.json["error"].lower()

        with app.app_context():
            assert User.query.filter_by(email="outro.auditor@test.com").first() is None

    def test_email_de_auditor_duplicado_retorna_400_e_nao_cria_selecao(
        self, app, client, db, organizer, token_organizer
    ):
        response = client.post(
            "/api/selection/",
            json=_payload(code="GER", auditor_email=organizer.email),
            headers={"Authorization": f"Bearer {token_organizer}"},
        )

        assert response.status_code == 400
        assert "e-mail" in response.json["error"].lower()

        with app.app_context():
            assert Selection.query.filter_by(code="GER").first() is None

    def test_selecao_criada_aparece_na_listagem_publica(self, client, token_organizer):
        client.post(
            "/api/selection/",
            json=_payload(code="POR", name="Portugal", auditor_email="auditor.por@test.com"),
            headers={"Authorization": f"Bearer {token_organizer}"},
        )

        response = client.get("/api/selection/")

        assert response.status_code == 200
        codigos = [item["code"] for item in response.json]
        assert "POR" in codigos
