from pathlib import Path
from google.cloud import storage

PROJECT_ID = "fifa-team-hub"
BUCKET_NAME = "fifa-team-hub-documents"

# Caminho absoluto até a raiz do projeto
ROOT_DIR = Path(__file__).resolve().parents[2]

# Caminho absoluto do JSON de credenciais
KEY_PATH = ROOT_DIR / "config" / "fifa-team-hub-key.json"


def get_bucket():
    client = storage.Client.from_service_account_json(
        str(KEY_PATH),
        project=PROJECT_ID
    )

    return client.bucket(BUCKET_NAME)


def test_gcs_bucket_connection():
    """
    Verifica se o bucket existe e se a aplicação
    consegue acessá-lo.
    """
    bucket = get_bucket()

    assert bucket.exists(), (
        f"Bucket '{BUCKET_NAME}' não encontrado."
    )

    print(f"\n✓ Conectado ao bucket {BUCKET_NAME}")


def test_gcs_upload_download():
    """
    Testa upload, download e remoção de um arquivo
    dentro do bucket.
    """
    bucket = get_bucket()

    blob = bucket.blob(
        "testes_desenvolvimento/conexao.txt"
    )

    try:
        mensagem = (
            "Conexão do FIFA Team Hub realizada com sucesso!"
        )

        blob.upload_from_string(mensagem)

        conteudo = blob.download_as_text()

        assert conteudo == mensagem

        print("\n✓ Upload e download funcionando.")

    finally:
        if blob.exists():
            blob.delete()

        print("✓ Arquivo de teste removido.")