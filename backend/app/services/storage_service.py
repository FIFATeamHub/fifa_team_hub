from abc import ABC, abstractmethod
from pathlib import Path
from datetime import timedelta
import uuid
import shutil
import os

import google.auth
from google.auth.transport import requests as google_auth_requests
from google.cloud import storage as gcs_storage
from werkzeug.utils import secure_filename

class StorageService(ABC):

    @abstractmethod
    def save_file(
        self,
        file_stream,
        stored_name: str,
        selection_id: str,
        content_type: str = None
    ) -> str:
        pass
        
    @abstractmethod
    def delete_file(
        self,
        storage_path: str
    ) -> None:
        pass
        
    @abstractmethod
    def get_signed_url(self, storage_path: str, document_id: str = None,expiration_minutes: int = 15) -> str:

        pass
    
    
    
class LocalStorageService(StorageService):
    def __init__(self, local_path: str = "./storage/uploads"):
        self.local_path = local_path
        os.makedirs(self.local_path, exist_ok=True)

    def save_file(
        self,
        file_stream,
        stored_name: str,
        selection_id: str,
        content_type: str = None
    ) -> str:
        # Content-Type não é persistido no storage local: quem serve o arquivo
        # (stream_local_file) usa send_file, que já infere o tipo pela extensão.
        safe_selection_id = os.path.basename(selection_id.strip())
        safe_stored_name = os.path.basename(stored_name.strip())

        if safe_selection_id != selection_id or safe_stored_name != stored_name:
            raise ValueError("Invalid path components")
            
        base_path = Path(self.local_path).resolve()
        safe_selection_id = secure_filename(str(selection_id))
        safe_stored_name = secure_filename(str(stored_name))

        if not safe_selection_id:
            raise ValueError("selection_id inválido")
        if not safe_stored_name:
            safe_stored_name = uuid.uuid4().hex
        target_dir = (base_path / safe_selection_id).resolve()
        target_dir.relative_to(base_path)

        target_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        file_path = (target_dir / safe_stored_name).resolve()
        file_path.relative_to(base_path)
        
        file_stream.seek(0)

        with open(file_path, "wb") as destination:
            shutil.copyfileobj(
                file_stream,
                destination
            )

        return str(file_path)

    def delete_file(
        self,
        storage_path: str
    ) -> None:

        path = Path(storage_path)

        if path.exists():
            path.unlink()
            
    def get_signed_url(self, storage_path: str, document_id: str = None, expiration_minutes: int = 15) -> str:

        # Armazenamento local não tem conceito de URL assinada pública: o arquivo
        # só pode ser servido através da rota autenticada de streaming.
        return f"/api/document/{document_id}/stream"
    



class GCSStorageService(StorageService):

    def __init__(self, bucket_name: str, project_id: str, public_url: str = None):

        self.bucket_name = bucket_name
        self.project_id = project_id
        self.public_url = public_url
        credentials, _ = google.auth.default()
        self.client = gcs_storage.Client(project=project_id, credentials=credentials)
        self.bucket = self.client.bucket(bucket_name)

    def save_file(self, file_stream, stored_name: str, selection_id: str, content_type: str = None) -> str:

        blob_path = f"{selection_id}/{stored_name}"
        blob = self.bucket.blob(blob_path)

        file_stream.seek(0)
        # Sem content_type explícito, o GCS grava o blob como
        # application/octet-stream: o navegador não consegue exibir o arquivo
        # inline (só baixa em silêncio) ao abrir a URL assinada em "Visualizar".
        blob.upload_from_file(file_stream, content_type=content_type)

        return f"gs://{self.bucket_name}/{blob_path}"
    



    def delete_file(self, storage_path: str) -> None:
        prefixo = f"gs://{self.bucket_name}/"
        if storage_path.startswith(prefixo):
            blob_path = storage_path.replace(prefixo, "")
            blob = self.bucket.blob(blob_path)
            if blob.exists():
                blob.delete()





    def get_signed_url(self, storage_path: str, document_id: str = None,expiration_minutes: int = 15) -> str:
        
        prefixo = f"gs://{self.bucket_name}/"
        if storage_path.startswith(prefixo):
            blob_path = storage_path.replace(prefixo, "")
        else:
            partes = storage_path.replace("\\", "/").split("/")
            blob_path = "/".join(partes[-2:]) if len(partes) >= 2 else partes[-1]

        blob = self.bucket.blob(blob_path)

        try:
            return blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=expiration_minutes),
                method="GET",
                api_access_endpoint=self.public_url
            )
        except AttributeError:
            credentials, _ = google.auth.default()
            credentials.refresh(google_auth_requests.Request())

            return blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=expiration_minutes),
                method="GET",
                service_account_email=credentials.service_account_email,
                access_token=credentials.token,
                api_access_endpoint=self.public_url
            )
