import pytest
import io
from unittest.mock import patch, MagicMock
from app.models import Document
from app.services.storage_service import GCSStorageService


class TestGCSIsolation:

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

    def test_upload_to_gcs_isolates_by_selection(self, client, token_bra_staff, mock_gcs_storage):
        response = client.post(
            "/api/document/upload",
            headers={"Authorization": f"Bearer {token_bra_staff}"},
            data={
                "doc_type": "CONVOCACAO",
                "file": (io.BytesIO(b"%PDF-1.4 test"), "test.pdf"),
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 201

        mock_gcs_storage.save_file.assert_called_once()
        assert mock_gcs_storage.save_file.call_args.kwargs["selection_id"] == "BRA"

    def test_cross_selection_document_access_denied_with_gcs(
        self, client, db, token_bra_staff, mock_gcs_storage
    ):
        arg_doc = self.create_test_document(
            db,
            id="arg-doc-123",
            selection_id="ARG",
            uploaded_by="user-arg",
            original_name="convocacao_arg.pdf",
            stored_name="arg-123.pdf",
            storage_path="gs://bucket/ARG/arg-123.pdf",
        )

        response = client.get(
            f"/documents/{arg_doc.id}/download",
            headers={"Authorization": f"Bearer {token_bra_staff}"}
        )

        assert response.status_code == 403
        mock_gcs_storage.get_signed_url.assert_not_called()

    def test_delete_from_gcs_when_document_deleted(self, client, db, token_bra_staff, mock_gcs_storage):
        doc = self.create_test_document(
            db,
            id="bra-doc-456",
            selection_id="BRA",
            storage_path="gs://bucket/BRA/doc.pdf",
        )

        response = client.delete(
            f"/documents/{doc.id}",
            headers={"Authorization": f"Bearer {token_bra_staff}"}
        )

        assert response.status_code == 204
        mock_gcs_storage.delete_file.assert_called_once_with("gs://bucket/BRA/doc.pdf")