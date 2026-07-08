import pytest
import io
from unittest.mock import patch, MagicMock
from app.models import Document
from app.services.storage_service import GCSStorageService


class TestGCSIsolation:

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

    def test_upload_to_gcs_isolates_by_selection(self, client, token_bra_staff, mock_gcs_storage, selection_bra):
        response = client.post(
            "/api/document/upload",
            headers={"Authorization": f"Bearer {token_bra_staff}"},
            data={
                "doc_type": "CONVOCADO",
                "file": (io.BytesIO(b"%PDF-1.4 test"), "test.pdf"),
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 201

        mock_gcs_storage.save_file.assert_called_once()
        assert mock_gcs_storage.save_file.call_args.kwargs["selection_id"] == str(selection_bra)

    def test_cross_selection_document_access_denied_with_gcs(
        self, client, db, token_bra_staff, mock_gcs_storage, selection_arg, arg_staff
    ):
        arg_doc = self.create_test_document(
            db,
            selection_id=selection_arg,
            uploaded_by=arg_staff.id,
            original_name="convocacao_arg.pdf",
            storage_path="gs://bucket/ARG/arg-123.pdf",
            storage_url="gs://bucket/ARG/arg-123.pdf",
        )

        response = client.get(
            f"/api/document/{arg_doc.id}/download",
            headers={"Authorization": f"Bearer {token_bra_staff}"}
        )
        assert response.status_code == 403
        mock_gcs_storage.get_signed_url.assert_not_called()    

    @pytest.mark.xfail(reason="DELETE ainda não implementado: route_delete_document é um stub que sempre retorna 200 e não chama storage.delete_file nem remove o registro do banco")
    def test_delete_from_gcs_when_document_deleted(self, client, db, token_bra_staff, mock_gcs_storage, selection_bra, bra_staff):
        doc = self.create_test_document(
            db,
            selection_id=selection_bra,
            uploaded_by=bra_staff.id,
            storage_path="gs://bucket/BRA/doc.pdf",
            storage_url="gs://bucket/BRA/doc.pdf",
        )

        response = client.delete(
            f"/api/document/{doc.id}",
            headers={"Authorization": f"Bearer {token_bra_staff}"}
        )

        assert response.status_code == 204
        mock_gcs_storage.delete_file.assert_called_once_with("gs://bucket/BRA/doc.pdf")