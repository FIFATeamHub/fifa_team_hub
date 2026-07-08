import pytest
import io
from unittest.mock import patch, MagicMock
from app.models import Document
from google.api_core.exceptions import ResourceExhausted

class TestGCSEdgeCases:

    @pytest.fixture
    def token_bra_staff(bra_staff_token):
        return bra_staff_token

    @pytest.fixture
    def mock_gcs_storage(self):
        with patch('app.services.storage_service.GCSStorageService') as mock_cls:
            service = MagicMock()
            service.save_file.return_value = "gs://bucket/BRA/doc.pdf"
            service.get_signed_url.return_value = "https://signed-url"
            mock_cls.return_value = service
            yield service

    @staticmethod
    def create_test_document(db, **overrides):
        defaults = dict(
            id="test-doc-id",
            selection_id="BRA",
            uploaded_by="user-bra",
            doc_type="CONVOCACAO",
            original_name="doc.pdf",
            stored_name="doc.pdf",
            storage_path="gs://bucket/BRA/doc.pdf",
            file_size_kb=100,
            mime_type="application/pdf",
            status="APPROVED"
        )
        defaults.update(overrides)
        doc = Document(**defaults)
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    def test_signed_url_expires_in_15_minutes(self, client, db, token_bra_staff, mock_gcs_storage):
        doc = self.create_test_document(db, selection_id="BRA")

        response = client.get(
            f"/documents/{doc.id}/download",
            headers={"Authorization": f"Bearer {token_bra_staff}"}
        )

        assert response.status_code == 200
        assert response.json()["expires_in_minutes"] == 15

    def test_gcs_quota_exceeded_returns_503(self, client, token_bra_staff, mock_gcs_storage):
        
        mock_gcs_storage.save_file.side_effect = ResourceExhausted("Quota exceeded")

        response = client.post(
            "/api/document/upload",
            headers={"Authorization": f"Bearer {token_bra_staff}"},
            data={
                "doc_type": "CONVOCACAO",
                "file": (io.BytesIO(b"test"), "test.pdf"),
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 503

    def test_gcs_blob_not_found_returns_410(self, client, db, token_bra_staff, mock_gcs_storage):
        from google.cloud.exceptions import NotFound

        doc = self.create_test_document(db, storage_path="gs://bucket/BRA/deleted.pdf")
        mock_gcs_storage.get_signed_url.side_effect = NotFound("Blob not found")

        response = client.get(
            f"/documents/{doc.id}/download",
            headers={"Authorization": f"Bearer {token_bra_staff}"}
        )

        assert response.status_code == 410