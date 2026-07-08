import os
import uuid
from datetime import timedelta
from functools import lru_cache
from typing import BinaryIO

from google.cloud import storage
from google.cloud.exceptions import NotFound


class GCSStorageService:
    def __init__(self, bucket_name: str | None = None):
        self.bucket_name = bucket_name or os.environ["GCS_BUCKET_NAME"]
        self._client = storage.Client()
        self._bucket = self._client.bucket(self.bucket_name)

    def save_file(self, file: BinaryIO, filename: str, selection_id: str) -> str:
        extension = os.path.splitext(filename)[1]
        stored_name = f"{uuid.uuid4().hex}{extension}"
        blob_path = f"{selection_id}/{stored_name}"

        blob = self._bucket.blob(blob_path)
        blob.upload_from_file(file, rewind=True)

        return f"gs://{self.bucket_name}/{blob_path}"

    def get_signed_url(self, storage_path: str, expiration_minutes: int = 15) -> str:
        blob = self._blob_from_storage_path(storage_path)
        return blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="GET",
        )

    def delete_file(self, storage_path: str) -> None:
        blob = self._blob_from_storage_path(storage_path)
        try:
            blob.delete()
        except NotFound:
            pass

    def _blob_from_storage_path(self, storage_path: str) -> storage.Blob:
        if not storage_path.startswith(f"gs://{self.bucket_name}/"):
            raise ValueError(f"storage_path fora do bucket configurado: {storage_path}")
        blob_path = storage_path.removeprefix(f"gs://{self.bucket_name}/")
        return self._bucket.blob(blob_path)


@lru_cache
def get_storage_service() -> GCSStorageService:

    return GCSStorageService()