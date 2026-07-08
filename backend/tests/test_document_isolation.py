import pytest
import io

@pytest.fixture
def token_bra_staff(bra_staff_token):
    return bra_staff_token

def test_upload_assigns_correct_selection_id(client, token_bra_staff):

    data = {
        "doc_type": "CONVOCADO",
        "file": (
            io.BytesIO(b"%PDF-1.4\n%%EOF"),
            "teste.pdf"
        )
    }

    response = client.post(
        "/api/document/upload",
        headers={
            "Authorization": f"Bearer {token_bra_staff}"
        },
        data=data,
        content_type="multipart/form-data"
    )

    assert response.status_code == 201


def test_bra_staff_cannot_see_arg_documents(client, token_bra_staff):

    response = client.get(
        "/api/document/",
        headers={
            "Authorization": f"Bearer {token_bra_staff}"
        }
    )

    assert response.status_code == 200

    for doc in response.json["data"]:
        assert doc["selection_code"] == "BRA"


def test_cross_selection_document_access_denied(
    client,
    token_bra_staff,
    arg_document_id
):

    response = client.get(
        f"/api/document/{arg_document_id}",
        headers={
            "Authorization": f"Bearer {token_bra_staff}"
        }
    )

    assert response.status_code == 403

@pytest.mark.xfail(reason="DELETE ainda não implementado")
def test_cross_selection_delete_denied(
    client,
    token_bra_staff,
    arg_document_id
):

    response = client.delete(
        f"/api/document/{arg_document_id}",
        headers={
            "Authorization": f"Bearer {token_bra_staff}"
        }
    )

    assert response.status_code == 403


def test_organizer_cannot_access_tactical_reports(
    client,
    token_organizer,
    arg_document_id
):

    response = client.get(
        f"/api/document/{arg_document_id}",
        headers={
            "Authorization": f"Bearer {token_organizer}"
        }
    )

    assert response.status_code == 403
