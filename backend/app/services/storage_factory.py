from app.services.storage_service import LocalStorageService, GCSStorageService
from flask import current_app

from flask import current_app
from app.services.storage_service import LocalStorageService, GCSStorageService

def get_storage_service():

    backend = current_app.config.get("STORAGE_BACKEND", "local").lower()

    if backend == "gcs":
        return GCSStorageService(
            bucket_name=current_app.config.get("GCS_BUCKET_NAME"),
            project_id=current_app.config.get("GCP_PROJECT_ID"),
        )

    return LocalStorageService(
        local_path=current_app.config.get(
            "LOCAL_STORAGE_PATH",
            "./storage/uploads"
        )
    )