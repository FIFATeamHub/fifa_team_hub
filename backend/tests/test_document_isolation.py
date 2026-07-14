import io
from uuid import UUID

from app.models.audit_log import AuditLog
from app.models.enums.user_role import LogAction

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
    
    
def test_download_url_registers_audit_log(
    app,
    client,
    token_arg_staff,
    arg_document_id,
):
    response = client.get(
        f"/api/document/{arg_document_id}/download",
        headers={
            "Authorization": f"Bearer {token_arg_staff}"
        }
    )

    assert response.status_code == 200

    with app.app_context():

        audit = AuditLog.query.filter_by(
            resource_id=UUID(arg_document_id),
            action=LogAction.DOWNLOAD
        ).first()

        assert audit is not None
        assert audit.action == LogAction.DOWNLOAD
        assert audit.status == "SUCCESS"
        assert audit.details.startswith("URL de download gerada")
        
def test_medical_staff_cannot_access_other_selection_document(
    client,
    token_bra_medical_staff,
    arg_document_id
):

    response = client.get(
        f"/api/document/{arg_document_id}",
        headers={
            "Authorization": f"Bearer {token_bra_medical_staff}"
        }
    )

    assert response.status_code == 403
    
def test_medical_staff_only_lists_documents_from_own_selection(
    client,
    token_bra_medical_staff
):

    response = client.get(
        "/api/document/",
        headers={
            "Authorization": f"Bearer {token_bra_medical_staff}"
        }
    )

    assert response.status_code == 200

    for document in response.json["data"]:
        assert document["selection_code"] == "BRA"
        
def test_auditor_cannot_access_other_selection_document(
    client,
    token_bra_auditor,
    arg_document_id
):

    response = client.get(
        f"/api/document/{arg_document_id}",
        headers={
            "Authorization": f"Bearer {token_bra_auditor}"
        }
    )

    assert response.status_code == 403
    
def test_auditor_only_lists_documents_from_own_selection(
    client,
    token_bra_auditor
):

    response = client.get(
        "/api/document/",
        headers={
            "Authorization": f"Bearer {token_bra_auditor}"
        }
    )

    assert response.status_code == 200

    for document in response.json["data"]:
        assert document["selection_code"] == "BRA"
        
def test_athlete_can_access_tactical_document_from_same_selection(
    client,
    token_bra_athlete,
    bra_document_id
):

    response = client.get(
        f"/api/document/{bra_document_id}",
        headers={
            "Authorization": f"Bearer {token_bra_athlete}"
        }
    )

    assert response.status_code == 200
    
def test_athlete_cannot_access_tactical_document_from_other_selection(
    client,
    token_bra_athlete,
    arg_document_id
):

    response = client.get(
        f"/api/document/{arg_document_id}",
        headers={
            "Authorization": f"Bearer {token_bra_athlete}"
        }
    )

    assert response.status_code == 403