import pytest
from unittest.mock import Mock, patch
from app.services.storage_service import GCSStorageService

@pytest.fixture
def gcs_service():
    with patch('google.cloud.storage.Client'), \
         patch('google.auth.default', return_value=(Mock(), "test-project")):
        return GCSStorageService(bucket_name="test-bucket", project_id="test-project")

def test_gcs_save_file(gcs_service):
    # 1. Preparação: Criamos o bloco de notas/dublê do arquivo (Blob)
    mock_blob = Mock()
    gcs_service.bucket.blob.return_value = mock_blob
    
    # 2. Execução: Simulamos o envio de um arquivo de bytes binários
    file_stream = Mock()
    result = gcs_service.save_file(file_stream, "document.pdf", "BRA")
    
    # 3. Validações (Assertions):
    assert result == "gs://test-bucket/BRA/document.pdf"
    
    file_stream.seek.assert_called_once_with(0)
    
    gcs_service.bucket.blob.assert_called_once_with("BRA/document.pdf")
    
    mock_blob.upload_from_file.assert_called_once_with(file_stream)

def test_gcs_get_signed_url(gcs_service):
    # 1. Preparação: Configura o que a função generate_signed_url deve simular
    mock_blob = Mock()
    mock_blob.generate_signed_url.return_value = "https://signed-url-example.com/token-secreto"
    gcs_service.bucket.blob.return_value = mock_blob
    
    # 2. Execução: Passa o caminho que estaria salvo no banco de dados
    url = gcs_service.get_signed_url("gs://test-bucket/BRA/document.pdf", expiration_minutes=15)
    
    # 3. Validações (Assertions):
    assert url == "https://signed-url-example.com/token-secreto"
    
    gcs_service.bucket.blob.assert_called_once_with("BRA/document.pdf")
    
    mock_blob.generate_signed_url.assert_called_once()

    assert mock_blob.generate_signed_url.call_args.kwargs["api_access_endpoint"] is None


def test_gcs_get_signed_url_uses_public_url_for_browser(gcs_service):
    gcs_service.public_url = "http://localhost:4443"

    mock_blob = Mock()
    mock_blob.generate_signed_url.return_value = "http://localhost:4443/test-bucket/BRA/document.pdf?token=..."
    gcs_service.bucket.blob.return_value = mock_blob

    url = gcs_service.get_signed_url("gs://test-bucket/BRA/document.pdf", expiration_minutes=15)

    assert url.startswith("http://localhost:4443/")
    assert mock_blob.generate_signed_url.call_args.kwargs["api_access_endpoint"] == "http://localhost:4443"


def test_gcs_delete_file(gcs_service):
    # 1. Preparação
    mock_blob = Mock()
    mock_blob.exists.return_value = True 
    gcs_service.bucket.blob.return_value = mock_blob
    
    # 2. Execução: Pede para deletar o arquivo do banco
    gcs_service.delete_file("gs://test-bucket/BRA/document.pdf")
    
    # 3. Validações (Assertions):
    gcs_service.bucket.blob.assert_called_once_with("BRA/document.pdf")
    
    mock_blob.delete.assert_called_once()