from pathlib import Path
from app.config import Config
import shutil


class StorageService:

    def save_file(
        self,
        file_stream,
        stored_name: str,
        selection_id: str
    ) -> str:
        raise NotImplementedError

    def delete_file(
        self,
        storage_path: str
    ) -> None:
        raise NotImplementedError
    
    
    
class LocalStorageService(StorageService):

    def save_file(
        self,
        file_stream,
        stored_name: str,
        selection_id: str
    ) -> str:

        target_dir = Path(Config.LOCAL_STORAGE_PATH) / selection_id

        target_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        file_path = target_dir / stored_name

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