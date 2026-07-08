import pytest
import io
from unittest.mock import patch, MagicMock
from app.models import Document
from google.api_core.exceptions import ResourceExhausted

class TestGCSEdgeCases:

    @pytest.fixture
    def app(self, app):
        app.config["STORAGE_BACKEND"] = "gcs"
        app.config["GCS_BUCKET_NAME"] = "test-bucket"
        app.config["GCP_PROJECT_ID"] = "test-project"
        return app

    @pytest.fixture
    def mock_gcs_storage(self):
        with patch('app.services.storage_factory.GCSStorageService') as mock_cls:
            service = MagicMock()
            service.save_file.return_value = "gs://bucket/BRA/doc.pdf"
            service.get_signed_url.return_value = "https://signed-url"
            mock_cls.return_value = service
            yield service

    @staticmethod
    def create_test_document(db, **overrides):
        import uuid as uuid_module
        from app.models.enums.user_role import TypeDocument, DocStatus
        defaults = dict(
            id=uuid_module.uuid4(),
            type=TypeDocument.CONVOCADO,
            original_name="doc.pdf",
            storage_path="gs://bucket/BRA/doc.pdf",
            storage_url="gs://bucket/BRA/doc.pdf",
            status=DocStatus.APPROVED.value
        )
        defaults.update(overrides)
        doc = Document(**defaults)
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    def test_signed_url_expires_in_15_minutes(self, client, db, token_bra_staff, mock_gcs_storage, selection_bra, bra_staff):
        doc = self.create_test_document(db, selection_id=selection_bra, uploaded_by=bra_staff.id)

        response = client.get(
            f"/api/document/{doc.id}/download",
            headers={"Authorization": f"Bearer {token_bra_staff}"}
        )

        assert response.status_code == 200
        assert response.json["expires_in_minutes"] == 15

    def test_gcs_quota_exceeded_returns_503(self, client, token_bra_staff, mock_gcs_storage):
        
        mock_gcs_storage.save_file.side_effect = ResourceExhausted("Quota exceeded")

        response = client.post(
            "/api/document/upload",
            headers={"Authorization": f"Bearer {token_bra_staff}"},
            data={
                "doc_type": "CONVOCADO",
                "file": (io.BytesIO(b"%PDF-1.4 test"), "test.pdf"),
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 503

    def test_gcs_blob_not_found_returns_410(self, client, db, token_bra_staff, mock_gcs_storage, selection_bra, bra_staff):
        from google.cloud.exceptions import NotFound

        doc = self.create_test_document(
            db, selection_id=selection_bra, uploaded_by=bra_staff.id,
            storage_path="gs://bucket/BRA/deleted.pdf", storage_url="gs://bucket/BRA/deleted.pdf"
        )
        mock_gcs_storage.get_signed_url.side_effect = NotFound("Blob not found")

        response = client.get(
            f"/api/document/{doc.id}/download",
            headers={"Authorization": f"Bearer {token_bra_staff}"}
        )

        assert response.status_code == 410