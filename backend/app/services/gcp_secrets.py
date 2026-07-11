import os
from google.cloud import secretmanager

def get_secret(secret_id: str, version_id: str = "latest") -> str:
    # Cria o cliente do Google
    client = secretmanager.SecretManagerServiceClient()
    
    # Precisamos do ID do seu projeto no GCP
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise ValueError("A variável GOOGLE_CLOUD_PROJECT precisa estar configurada para buscar segredos.")

    # Constrói o nome oficial do secret na GCP
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    
    # Acessa o valor no cofre
    response = client.access_secret_version(request={"name": name})
    
    # Retorna o valor decodificando os bytes
    return response.payload.data.decode("UTF-8")
