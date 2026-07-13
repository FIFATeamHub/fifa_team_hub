import io
from uuid import UUID

from app.extensions import db
from app.models.document import Document
from app.models.audit_log import AuditLog
from app.models.enums.user_role import TypeDocument, DocStatus, LogAction


def test_auditor_upload_passport_stays_pending(app, client, token_auditor):

    data = {
        "doc_type": "PASSPORT",
        "file": (
            io.BytesIO(b"%PDF-1.4\n%%EOF"),
            "passport.pdf"
        )
    }

    response = client.post(
        "/api/document/upload",
        headers={"Authorization": f"Bearer {token_auditor}"},
        data=data,
        content_type="multipart/form-data"
    )

    assert response.status_code == 201
    document_id = response.get_json()["id"]

    with app.app_context():
        documento = Document.query.get(UUID(document_id))
        assert documento.status == DocStatus.PENDING.value


def test_technical_staff_upload_convocado_auto_approves(app, client, token_bra_staff):

    data = {
        "doc_type": "CONVOCADO",
        "file": (
            io.BytesIO(b"%PDF-1.4\n%%EOF"),
            "convocado.pdf"
        )
    }

    response = client.post(
        "/api/document/upload",
        headers={"Authorization": f"Bearer {token_bra_staff}"},
        data=data,
        content_type="multipart/form-data"
    )

    assert response.status_code == 201
    document_id = response.get_json()["id"]

    with app.app_context():
        documento = Document.query.get(UUID(document_id))
        assert documento.status == DocStatus.APPROVED.value


def test_review_blocks_self_review(app, client, auditor, token_auditor):

    with app.app_context():
        documento = Document(
            uploaded_by=auditor.id,
            type=TypeDocument.PASSPORT,
            original_name="passport.pdf",
            storage_path="/tmp/passport.pdf",
            status=DocStatus.PENDING.value
        )
        db.session.add(documento)
        db.session.commit()
        document_id = str(documento.id)

    response = client.patch(
        f"/api/document/{document_id}/review",
        headers={"Authorization": f"Bearer {token_auditor}"},
        json={"status": "APPROVED"}
    )

    assert response.status_code == 403

    with app.app_context():
        documento_atual = Document.query.get(UUID(document_id))
        assert documento_atual.status == DocStatus.PENDING.value
        assert documento_atual.reviewed_by is None


def test_review_success_by_different_auditor(app, client, auditor, bra_auditor, token_bra_auditor):

    with app.app_context():
        documento = Document(
            uploaded_by=auditor.id,
            type=TypeDocument.PASSPORT,
            original_name="passport.pdf",
            storage_path="/tmp/passport.pdf",
            status=DocStatus.PENDING.value
        )
        db.session.add(documento)
        db.session.commit()
        document_id = str(documento.id)

    response = client.patch(
        f"/api/document/{document_id}/review",
        headers={"Authorization": f"Bearer {token_bra_auditor}"},
        json={"status": "APPROVED"}
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "APPROVED"
    assert body["reviewed_by"] == str(bra_auditor.id)

    with app.app_context():
        documento_atualizado = Document.query.get(UUID(document_id))
        assert documento_atualizado.status == DocStatus.APPROVED.value
        assert documento_atualizado.reviewed_by == bra_auditor.id
        assert documento_atualizado.reviewed_at is not None

        audit = AuditLog.query.filter_by(
            resource_id=UUID(document_id),
            action=LogAction.REVIEW,
            status="SUCCESS"
        ).first()

        assert audit is not None
        assert audit.user_id == bra_auditor.id
