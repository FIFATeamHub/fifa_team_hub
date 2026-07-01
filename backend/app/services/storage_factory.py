import os
from app.services.storage_service import LocalStorageService, GCSStorageService

def get_storage_service():
    
    backend = os.getenv("STORAGE_BACKEND", "local").lower()
    
    if backend == "gcs":
        
        bucket_name = os.getenv("GCS_BUCKET_NAME")
        project_id = os.getenv("GCP_PROJECT_ID")
        return GCSStorageService(bucket_name=bucket_name, project_id=project_id)
        
    

    local_path = os.getenv("LOCAL_STORAGE_PATH", "./storage/uploads")
    return LocalStorageService(local_path=local_path)