from abc import ABC, abstractmethod
from pathlib import Path
from datetime import timedelta
import shutil
import os

from google.cloud import storage as gcs_storage

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

        base_dir = Path(self.local_path).resolve()
        target_dir = (base_dir / safe_selection_id).resolve()
        target_dir.relative_to(base_dir)

        target_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        file_path = (target_dir / safe_stored_name).resolve()
        file_path.relative_to(base_dir)
        
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
            
    def get_signed_url(self, storage_path: str, expiration_minutes: int = 15) -> str:
        path = Path(storage_path)

        if len(path.parts) >= 2:
            return f"/static/uploads/{path.parts[-2]}/{path.parts[-1]}"

        return f"/static/uploads/{path.name}"
    



class GCSStorageService(StorageService):

    def __init__(self, bucket_name: str, project_id: str):
            
        self.bucket_name = bucket_name
        self.project_id = project_id
        # Inicializa o cliente vinculando diretamente ao ID do projeto correto
        self.client = gcs_storage.Client(project=project_id)
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
        
        # Solicita à API do Google a geração do link temporário assinado criptograficamente
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="GET"
        )
        return url
