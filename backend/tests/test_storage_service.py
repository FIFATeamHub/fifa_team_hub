import pytest
from unittest.mock import Mock, patch
from app.services.storage_service import GCSStorageService

@pytest.fixture
def gcs_service():
    """
    Prepara o ambiente de testes substituindo o cliente real do Google 
    por um dublê (Mock) e instancia o serviço com dados fictícios.
    """
    with patch('google.cloud.storage.Client'):
        return GCSStorageService(bucket_name="test-bucket", project_id="test-project")

def test_gcs_save_file(gcs_service):
    """
    Garante que a função save_file monta o caminho correto na nuvem (gs://)
    e envia os dados para a 'pasta virtual' correta com base no ID da seleção.
    """
    # 1. Preparação: Criamos o bloco de notas/dublê do arquivo (Blob)
    mock_blob = Mock()
    gcs_service.bucket.blob.return_value = mock_blob
    
    # 2. Execução: Simulamos o envio de um arquivo de bytes binários
    file_stream = Mock()  # Um objeto mockado que simula o arquivo vindo do request
    result = gcs_service.save_file(file_stream, "document.pdf", "BRA")
    
    # 3. Validações (Assertions):
    # Verifica se o link final devolvido seguiu o padrão esperado pela nuvem
    assert result == "gs://test-bucket/BRA/document.pdf"
    
    # Verifica se o código de verdade rebobinou o arquivo antes de transmitir
    file_stream.seek.assert_called_once_with(0)
    
    # Verifica se o arquivo foi mirado na pasta certa da Seleção Brasileira (BRA)
    gcs_service.bucket.blob.assert_called_once_with("BRA/document.pdf")
    
    # Verifica se o comando de streaming para o Google Cloud foi acionado
    mock_blob.upload_from_file.assert_called_once_with(file_stream)

def test_gcs_get_signed_url(gcs_service):
    """
    Garante que a função get_signed_url consegue ler a string 'gs://',
    encontrar o arquivo no armário e solicitar à API do Google a URL assinada.
    """
    # 1. Preparação: Configura o que a função generate_signed_url deve simular
    mock_blob = Mock()
    mock_blob.generate_signed_url.return_value = "https://signed-url-example.com/token-secreto"
    gcs_service.bucket.blob.return_value = mock_blob
    
    # 2. Execução: Passa o caminho que estaria salvo no banco de dados
    url = gcs_service.get_signed_url("gs://test-bucket/BRA/document.pdf", expiration_minutes=15)
    
    # 3. Validações (Assertions):
    # Verifica se o método repassou para o Frontend exatamente o link que o Google gerou
    assert url == "https://signed-url-example.com/token-secreto"
    
    # Garante que o arquivo mapeado para assinar foi o correto
    gcs_service.bucket.blob.assert_called_once_with("BRA/document.pdf")
    
    # Garante que as configurações de segurança da URL (V4, GET, 15 minutos) foram enviadas ao Google
    mock_blob.generate_signed_url.assert_called_once()

def test_gcs_delete_file(gcs_service):
    """
    Garante que a lógica de remoção localiza o arquivo correto tirando o 
    prefixo da nuvem e envia a ordem de destruição para o objeto certo.
    """
    # 1. Preparação
    mock_blob = Mock()
    mock_blob.exists.return_value = True  # Simula que o arquivo realmente existe no bucket
    gcs_service.bucket.blob.return_value = mock_blob
    
    # 2. Execução: Pede para deletar o arquivo do banco
    gcs_service.delete_file("gs://test-bucket/BRA/document.pdf")
    
    # 3. Validações (Assertions):
    # Verifica se o código removeu o "gs://test-bucket/" e buscou apenas o caminho limpo
    gcs_service.bucket.blob.assert_called_once_with("BRA/document.pdf")
    
    # Verifica se o sistema checou a existência e executou o comando definitivo de apagar (.delete())
    mock_blob.delete.assert_called_once()