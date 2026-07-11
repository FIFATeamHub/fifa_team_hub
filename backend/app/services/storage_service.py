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
        selection_id: str
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
        #Gera URL temporária assinada (apenas GCS)
        pass
    
    
    
class LocalStorageService(StorageService):
    def __init__(self, local_path: str = "./storage/uploads"):
        self.local_path = local_path
        # Garante que a pasta raiz do storage exista localmente
        os.makedirs(self.local_path, exist_ok=True)

    def save_file(
        self,
        file_stream,
        stored_name: str,
        selection_id: str
    ) -> str:
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

        path = Path(storage_path)

        if len(path.parts) >= 2:
            return f"/static/uploads/{path.parts[-2]}/{path.parts[-1]}"

        return f"/static/uploads/{path.name}"
    



class GCSStorageService(StorageService):

    def __init__(self, bucket_name: str, project_id: str, public_url: str = None):

        self.bucket_name = bucket_name
        self.project_id = project_id
        # Host usado apenas para montar a signed URL devolvida ao navegador (ex:
        # http://localhost:4443 em dev com fake-gcs). O backend continua falando
        # com o storage via STORAGE_EMULATOR_HOST normalmente; None preserva o
        # comportamento padrão (client.api_endpoint / storage.googleapis.com).
        self.public_url = public_url
        # Credenciais explícitas: quando STORAGE_EMULATOR_HOST está setado (dev local
        # com fake-gcs), o SDK ignora silenciosamente as credenciais padrão e força
        # AnonymousCredentials, o que quebra generate_signed_url() (sem chave privada)
        # e derruba o fallback para a IAM SignBlob API real do Google. Passando as
        # credenciais explicitamente, a assinatura V4 é feita localmente com a chave
        # privada da service account, sem depender de rede externa.
        credentials, _ = google.auth.default()
        self.client = gcs_storage.Client(project=project_id, credentials=credentials)
        self.bucket = self.client.bucket(bucket_name)

    def save_file(self, file_stream, stored_name: str, selection_id: str) -> str:

        blob_path = f"{selection_id}/{stored_name}"
        blob = self.bucket.blob(blob_path)
        
       
        file_stream.seek(0)
        blob.upload_from_file(file_stream)
        
        return f"gs://{self.bucket_name}/{blob_path}"
    



    def delete_file(self, storage_path: str) -> None:
        # Extrai o caminho relativo tirando o 'gs://nome-do-bucket/'
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
            # Fallback caso apenas o caminho interno sem o gs:// tenha sido passado
            partes = storage_path.replace("\\", "/").split("/")
            blob_path = "/".join(partes[-2:]) if len(partes) >= 2 else partes[-1]

        blob = self.bucket.blob(blob_path)

        try:
            # Caminho padrão: funciona quando as credenciais têm chave privada
            # (ex: GOOGLE_APPLICATION_CREDENTIALS com JSON de service account, em dev local)
            return blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=expiration_minutes),
                method="GET",
                api_access_endpoint=self.public_url
            )
        except AttributeError:
            # Credenciais do metadata server (Cloud Run/GCE) não têm chave privada.
            # Assina via IAM SignBlob API usando a identidade da própria service account.
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
