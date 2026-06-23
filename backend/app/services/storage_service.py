import os
from abc import ABC, abstractmethod
from google.cloud import storage as gcs_storage
from datetime import timedelta

class StorageService(ABC):

    #Interface abstrata (Contrato) que define o comportamento esperado 

    @abstractmethod
    def save_file(self, file_stream, stored_name: str, selection_id: str) -> str:
        pass
       
    @abstractmethod
    def delete_file(self, storage_path: str) -> None:
        pass
       
    @abstractmethod
    def get_signed_url(self, storage_path: str, document_id: str = None,expiration_minutes: int = 15) -> str:
        #Gera URL temporária assinada (apenas GCS)
        pass




class LocalStorageService(StorageService):

    #Implementação para armazenamento em disco local (Desenvolvimento/Testes).

    def __init__(self, local_path: str = "./storage/uploads"):
        self.local_path = local_path
        # Garante que a pasta raiz do storage exista localmente
        os.makedirs(self.local_path, exist_ok=True)




    def save_file(self, file_stream, stored_name: str, selection_id: str) -> str:
        """
        Salva o arquivo no disco local dentro da pasta da seleção:
        Ex: ./storage/uploads/selection_id/nome_unico.pdf
        """
        # Cria a subpasta com o ID da seleção, se não existir

        pasta_selecao = os.path.join(self.local_path, selection_id)
        os.makedirs(pasta_selecao, exist_ok=True)
        
        caminho_final = os.path.join(pasta_selecao, stored_name)
        
        # Reseta o ponteiro do arquivo recebido e grava o binário no disco
        file_stream.seek(0)
        with open(caminho_final, "wb") as f:
            f.write(file_stream.read())
            
        return caminho_final




    def delete_file(self, storage_path: str) -> None:                       # IMPLEMENTAR NO ENDPOINT DELETE
  
        if os.path.exists(storage_path):
            os.remove(storage_path)




    def get_signed_url(self, storage_path: str, document_id: str = None, expiration_minutes: int = 15) -> str:
        
        if document_id:
            return f"/document/{document_id}/stream"
        return "/document/unknown/stream"
    



class GCSStorageService(StorageService):

    def __init__(self, bucket_name: str, project_id: str):
            
        self.bucket_name = bucket_name
        self.project_id = project_id
        # Inicializa o cliente vinculando diretamente ao ID do projeto correto
        self.client = gcs_storage.Client(project=project_id)
        self.bucket = self.client.bucket(bucket_name)

    def save_file(self, file_stream, stored_name: str, selection_id: str) -> str:
        """
        Envia o arquivo para o bucket organizando pelo ID da seleção como pasta virtual.
        Retorna o caminho universal do objeto: gs://nome-do-bucket/selection_id/nome_unico.pdf
        """

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