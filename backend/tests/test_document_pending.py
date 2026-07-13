from app.extensions import db
from app.models.document import Document
from app.models.enums.user_role import TypeDocument, DocStatus


def test_list_pending_documents(client, app, bra_athlete, token_bra_athlete, selection_bra):

    with app.app_context():

        passport = Document(
            selection_id=selection_bra,
            uploaded_by=bra_athlete.id,
            type=TypeDocument.PASSPORT,
            original_name="passport.pdf",
            storage_path="/tmp/passport.pdf",
            status=DocStatus.APPROVED.value
        )

        db.session.add(passport)
        db.session.commit()

    response = client.get(
        "/api/document/pending",
        headers={
            "Authorization": f"Bearer {token_bra_athlete}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    returned_types = {
        item["doc_type"]
        for item in data
    }

    assert "CONVOCADO" in returned_types
    assert "LAUDO_MEDICO" in returned_types

    assert "PASSPORT" not in returned_types
    
def test_list_pending_documents_when_user_has_no_documents(
    client,
    token_bra_athlete
):

    response = client.get(
        "/api/document/pending",
        headers={
            "Authorization": f"Bearer {token_bra_athlete}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    returned_types = {
        item["doc_type"]
        for item in data
    }

    assert returned_types == {
        "PASSPORT",
        "CONVOCADO",
        "LAUDO_MEDICO"
    }