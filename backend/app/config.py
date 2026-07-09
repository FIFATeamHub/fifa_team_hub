import os
from dotenv import load_dotenv

load_dotenv()


class Config():
    
    def __init__(self):
        pass
    
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    STORAGE_BACKEND = os.getenv(
        "STORAGE_BACKEND",
        "local"
    )

    LOCAL_STORAGE_PATH = os.getenv(
        "LOCAL_STORAGE_PATH",
        "./storage/uploads"
    )

    MAX_FILE_SIZE_BYTES = (
        int(os.getenv("MAX_FILE_SIZE_MB", 10))
        * 1024
        * 1024
    )

    ALLOWED_EXTENSIONS = set(
        os.getenv(
            "ALLOWED_EXTENSIONS",
            "pdf,jpg,jpeg,png,docx"
        ).split(",")
    )
    
def check_required_env_vars():
    # lista de variaveis 
    required_vars = [
        "SECRET_KEY",
        "DATABASE_URL",
        "JWT_SECRET_KEY"
    ]

    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        raise RuntimeError(f"FALHA FATAL DE STARTUP: Faltam as seguintes variáveis "
            f"obrigatórias em produção: {', '.join(missing)}"
        )
    
    if os.getenv("STORAGE_BACKEND") == "gcs":
        required_gcs = ["GCS_BUCKET_NAME", "GOOGLE_APPLICATION_CREDENTIALS"]
        missing_gcs = [var for var in required_gcs if not os.getenv(var)]

        if missing_gcs:
            raise RuntimeError(
                f"FALHA FATAL DE STORAGE: O STORAGE_BACKEND está definido como 'gcs', "
                f"mas faltam as configurações da nuvem: {', '.join(missing_gcs)}"
            )