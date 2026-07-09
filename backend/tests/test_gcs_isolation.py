import io

from app.models.enums.user_role import LogAction
from tests.conftest import create_test_document, get_latest_audit_log


class TestGCSIsolation:
    """Testes que garantem isolamento mesmo com GCS."""

    def test_upload_to_gcs_isolates_by_selection(
        self, gcs_client, db, token_bra_staff, mock_gcs_storage, selection_bra, bra_staff
    ):
        """Upload de BRA vai para gs://bucket/BRA/* e registra AuditLog de sucesso."""
        response = gcs_client.post(
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
        save_kwargs = mock_gcs_storage.save_file.call_args.kwargs
        assert save_kwargs["selection_id"] == str(selection_bra)
        assert save_kwargs["stored_name"]
        assert save_kwargs["file_stream"] is not None

        audit_log = get_latest_audit_log(db, action=LogAction.UPLOAD, user_id=bra_staff.id)
        assert audit_log is not None
        assert audit_log.status == "SUCCESS"
        assert audit_log.action == LogAction.UPLOAD

    def test_cross_selection_document_access_denied_with_gcs(
        self, gcs_client, db, token_bra_staff, mock_gcs_storage, selection_arg, arg_staff, bra_staff
    ):
        """BRA não consegue acessar documento ARG mesmo em GCS."""
        arg_doc = create_test_document(
            db,
            selection_id=selection_arg,
            uploaded_by=arg_staff.id,
            original_name="convocacao_arg.pdf",
            storage_path="gs://bucket/ARG/arg-123.pdf",
            storage_url="gs://bucket/ARG/arg-123.pdf",
        )

        response = gcs_client.get(
            f"/api/document/{arg_doc.id}/download",
            headers={"Authorization": f"Bearer {token_bra_staff}"},
        )

        assert response.status_code == 403
        mock_gcs_storage.get_signed_url.assert_not_called()

        audit_log = get_latest_audit_log(
            db, action=LogAction.ACCESS_DENIED, user_id=bra_staff.id, status="FAILURE"
        )
        assert audit_log is not None
        assert str(audit_log.resource_id) == str(arg_doc.id)

    def test_delete_from_gcs_when_document_deleted(
        self, gcs_client, db, token_bra_staff, mock_gcs_storage, selection_bra, bra_staff
    ):
        """DELETE /api/document/{id} deleta blob do GCS e registra AuditLog."""
        doc = create_test_document(
            db,
            selection_id=selection_bra,
            uploaded_by=bra_staff.id,
            storage_path="gs://bucket/BRA/doc.pdf",
            storage_url="gs://bucket/BRA/doc.pdf",
        )

        response = gcs_client.delete(
            f"/api/document/{doc.id}",
            headers={"Authorization": f"Bearer {token_bra_staff}"},
        )

        assert response.status_code == 204
        mock_gcs_storage.delete_file.assert_called_once_with("gs://bucket/BRA/doc.pdf")

        audit_log = get_latest_audit_log(db, action=LogAction.DELETE, user_id=bra_staff.id)
        assert audit_log is not None
        assert audit_log.status == "SUCCESS"
        assert str(audit_log.resource_id) == str(doc.id)
