import io

from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable
from google.cloud.exceptions import NotFound

from app.models.enums.user_role import LogAction
from tests.conftest import create_test_document, get_latest_audit_log


class TestGCSEdgeCases:
    """Casos edge de GCS: URLs expiradas, blobs deletados, quotas e conectividade."""

    def test_signed_url_expires_in_15_minutes(
        self, gcs_client, db, token_bra_staff, mock_gcs_storage, selection_bra, bra_staff
    ):
        """URL assinada válida por exatamente 15 minutos."""
        doc = create_test_document(db, selection_id=selection_bra, uploaded_by=bra_staff.id)

        response = gcs_client.get(
            f"/api/document/{doc.id}/download",
            headers={"Authorization": f"Bearer {token_bra_staff}"},
        )

        assert response.status_code == 200
        assert response.json["expires_in_minutes"] == 15

        mock_gcs_storage.get_signed_url.assert_called_once_with(
            storage_path="gs://bucket/BRA/doc.pdf",
            document_id=str(doc.id),
            expiration_minutes=15,
        )

        audit_log = get_latest_audit_log(db, action=LogAction.DOWNLOAD, user_id=bra_staff.id)
        assert audit_log is not None
        assert audit_log.status == "SUCCESS"

    def test_gcs_quota_exceeded_returns_503(
        self, gcs_client, db, token_bra_staff, mock_gcs_storage, bra_staff
    ):
        """Se GCS retorna erro de quota, retornar 503 e registrar falha no AuditLog."""
        mock_gcs_storage.save_file.side_effect = ResourceExhausted("Quota exceeded")

        response = gcs_client.post(
            "/api/document/upload",
            headers={"Authorization": f"Bearer {token_bra_staff}"},
            data={
                "doc_type": "CONVOCADO",
                "file": (io.BytesIO(b"%PDF-1.4 test"), "test.pdf"),
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 503

        audit_log = get_latest_audit_log(
            db, action=LogAction.UPLOAD, user_id=bra_staff.id, status="FAILURE"
        )
        assert audit_log is not None
        assert "cota" in audit_log.details.lower()

    def test_gcs_blob_not_found_returns_410(
        self, gcs_client, db, token_bra_staff, mock_gcs_storage, selection_bra, bra_staff
    ):
        """Se blob foi deletado externamente, retornar 410 Gone."""
        doc = create_test_document(
            db,
            selection_id=selection_bra,
            uploaded_by=bra_staff.id,
            storage_path="gs://bucket/BRA/deleted.pdf",
            storage_url="gs://bucket/BRA/deleted.pdf",
        )
        mock_gcs_storage.get_signed_url.side_effect = NotFound("Blob not found")

        response = gcs_client.get(
            f"/api/document/{doc.id}/download",
            headers={"Authorization": f"Bearer {token_bra_staff}"},
        )

        assert response.status_code == 410

        audit_log = get_latest_audit_log(
            db, action=LogAction.ACCESS_DENIED, user_id=bra_staff.id, status="FAILURE"
        )
        assert audit_log is not None
        assert "não encontrado" in audit_log.details.lower()

    def test_gcs_connectivity_error_returns_503(
        self, gcs_client, db, token_bra_staff, mock_gcs_storage, selection_bra, bra_staff
    ):
        """Erro de conectividade com GCS retorna 503 e registra falha no AuditLog."""
        doc = create_test_document(db, selection_id=selection_bra, uploaded_by=bra_staff.id)
        mock_gcs_storage.get_signed_url.side_effect = ServiceUnavailable("Connection refused")

        response = gcs_client.get(
            f"/api/document/{doc.id}/download",
            headers={"Authorization": f"Bearer {token_bra_staff}"},
        )

        assert response.status_code == 503
        assert "indisponível" in response.json["error"].lower()

        audit_log = get_latest_audit_log(
            db, action=LogAction.ACCESS_DENIED, user_id=bra_staff.id, status="FAILURE"
        )
        assert audit_log is not None
        assert "indisponível" in audit_log.details.lower()
