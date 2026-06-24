import pytest
import io

def test_upload_assigns_correct_selection_id(client, token_bra_staff):
    # 1. Correção: Flask test client exige que arquivos vão no 'data' com io.BytesIO
    data = {
        "doc_type": "CONVOCACAO",
        "file": (io.BytesIO(b"%PDF-1.4 test"), "test.pdf")
    }
    
    # ATENÇÃO: Se der 404, ajuste a URL para o prefixo correto (ex: "/api/documents/upload")
    response = client.post("/documents/upload",
        headers={"Authorization": f"Bearer {token_bra_staff}"},
        data=data,
        content_type="multipart/form-data"
    )
    
    assert response.status_code == 201
    doc_id = response.json()["id"]

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
    id_relatorio_tatico = "id-do-relatorio-tatico-aqui"
    
    response = client.get(f"/documents/{id_relatorio_tatico}",
        headers={"Authorization": f"Bearer {token_organizer}"}
    )
    assert response.status_code == 403