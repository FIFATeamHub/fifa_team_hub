import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_upload_assigns_correct_selection_id(client, token_bra_staff):
    response = client.post("/documents/upload",
        headers={"Authorization": f"Bearer {token_bra_staff}"},
        data={"doc_type": "CONVOCACAO"},
        files={"file": ("test.pdf", b"%PDF-1.4 test", "application/pdf")}
    )
    assert response.status_code == 201
    doc_id = response.json()["id"]
    doc = db.query(Document).filter_by(id=doc_id).first()
    assert str(doc.selection_id) == BRA_SELECTION_ID

def test_bra_staff_cannot_see_arg_documents(client, token_bra_staff):
    response = client.get("/documents",
        headers={"Authorization": f"Bearer {token_bra_staff}"}
    )
    assert response.status_code == 200
    for doc in response.json()["data"]:
        assert doc["selection_code"] == "BRA"

def test_cross_selection_document_access_denied(client, token_bra_staff, arg_document_id):
    response = client.get(f"/documents/{arg_document_id}",
        headers={"Authorization": f"Bearer {token_bra_staff}"}
    )
    assert response.status_code == 403

def test_cross_selection_delete_denied(client, token_bra_staff, arg_document_id):
    response = client.delete(f"/documents/{arg_document_id}",
        headers={"Authorization": f"Bearer {token_bra_staff}"}
    )
    assert response.status_code == 403

def test_organizer_cannot_access_tactical_reports(client, token_organizer):
    dados_documento = {
        "tipo": "RELATORIO_TATICO",
        "titulo": "Análise de Risco",
        "conteudo": "Estratégia"
    }
    resposta_criacao = client.post("/api/documentos", json=dados_documento)
    id_documento = resposta_criacao.json().get("id")
    
    cabecalhos = {
        "Authorization": f"Bearer {token_organizer}"
    }
    response = client.get(f"/api/documentos/{id_documento}", headers=cabecalhos)

    assert response.status_code == 403
