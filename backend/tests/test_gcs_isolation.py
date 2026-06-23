import pytest
from unittest.mock import patch, MagicMock
from app.models import Document
 
class TestGCSIsolation:    
    @pytest.fixture
    def mock_gcs_storage(self):
        with patch('app.services.storage_service.GCSStorageService') as mock_cls:
            service = MagicMock()
            service.save_file.return_value = "gs://bucket/BRA/doc.pdf"
            service.get_signed_url.return_value = "https://signed-url"
            mock_cls.return_value = service
            yield service
    
    def test_upload_to_gcs_isolates_by_selection(self, client, token_bra_staff, mock_gcs_storage):
        #Upload de BRA vai para gs://bucket/BRA/
        response = client.post(
            "/documents/upload",
            headers={"Authorization": f"Bearer {token_bra_staff}"},
            data={"doc_type": "CONVOCACAO"},
            files={"file": ("test.pdf", b"%PDF-1.4 test")}
        )
        
        assert response.status_code == 201
        
        # Verificar que save_file foi chamado com selection_id=BRA
        mock_gcs_storage.save_file.assert_called_once()
        call_args = mock_gcs_storage.save_file.call_args
        assert call_args[0][2] == "BRA"  # selection_id como 3º arg
    
    def test_cross_selection_document_access_denied_with_gcs(
        self, client, token_bra_staff, mock_gcs_storage
    ):
        #BRA não consegue acessar documento ARG mesmo em GCS
        # Simular documento ARG no banco
        arg_doc = Document(
            id="arg-doc-123",
            selection_id="ARG",
            uploaded_by="user-arg",
            doc_type="CONVOCACAO",
            original_name="convocacao_arg.pdf",
            stored_name="arg-123.pdf",
            storage_path="gs://bucket/ARG/arg-123.pdf",
            file_size_kb=100,
            mime_type="application/pdf",
            status="APPROVED"
        )
        db.add(arg_doc)
        db.commit()
        
        # Tentar download com token BRA
        response = client.get(
            f"/documents/arg-doc-123/download",
            headers={"Authorization": f"Bearer {token_bra_staff}"}
        )
        
        assert response.status_code == 403
        # Verificar que get_signed_url NÃO foi chamado
        mock_gcs_storage.get_signed_url.assert_not_called()
    
    def test_delete_from_gcs_when_document_deleted(self, client, token_bra_staff, mock_gcs_storage):
        #DELETE /documents/{id} deleta blob do GCS
        doc = create_test_document(
            selection_id="BRA",
            storage_path="gs://bucket/BRA/doc.pdf"
        )
        
        response = client.delete(
            f"/documents/{doc.id}",
            headers={"Authorization": f"Bearer {token_bra_staff}"}
        )
        
        assert response.status_code == 204
        # Verificar que delete_file foi chamado
        mock_gcs_storage.delete_file.assert_called_once_with("gs://bucket/BRA/doc.pdf")

# ---------------------------Testes de Egde Cases---------------------------

    def test_signed_url_expires_in_15_minutes(self, client, token_bra_staff):
        """URL assinada válida por exatamente 15 minutos"""
        doc = create_test_document(selection_id="BRA")
        
        response = client.get(
            f"/documents/{doc.id}/download",
            headers={"Authorization": f"Bearer {token_bra_staff}"}
        )
        
        assert response.json["expires_in_minutes"] == 15
    
    def test_gcs_quota_exceeded_returns_503(self, client, token_bra_staff, mock_gcs_storage):
        """Se GCS retorna erro de quota, retornar 503"""
        from google.api_core.exceptions import QuotaExceeded
        
        mock_gcs_storage.save_file.side_effect = QuotaExceeded("Quota exceeded")
        
        response = client.post(
            "/documents/upload",
            headers={"Authorization": f"Bearer {token_bra_staff}"},
            data={"doc_type": "CONVOCACAO"},
            files={"file": ("test.pdf", b"test")}
        )
        
        assert response.status_code == 503
    
    def test_gcs_blob_not_found_returns_410(self, client, token_bra_staff, mock_gcs_storage):
        """Se blob foi deletado externamente, retornar 410 Gone"""
        from google.cloud.exceptions import NotFound
        
        doc = create_test_document(storage_path="gs://bucket/BRA/deleted.pdf")
        mock_gcs_storage.get_signed_url.side_effect = NotFound("Blob not found")
        
        response = client.get(
            f"/documents/{doc.id}/download",
            headers={"Authorization": f"Bearer {token_bra_staff}"}
        )
        
        assert response.status_code == 410