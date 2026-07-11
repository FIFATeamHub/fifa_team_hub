import os
from dotenv import load_dotenv

load_dotenv()


class Config():

    def __init__(self):
        pass

    is_production = bool(os.getenv("GOOGLE_CLOUD_PROJECT"))

    if is_production:
        from app.services.gcp_secrets import get_secret

        SECRET_KEY = get_secret("JWT_SECRET_KEY")
        db_user = os.getenv("DB_USER", "postgres")
        db_pass = get_secret("DB_PASSWORD")
        db_name = os.getenv("DB_NAME", "postgres")
        db_instance_name = os.getenv("CLOUD_SQL_INSTANCE_NAME")
        SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{db_user}:{db_pass}@/{db_name}?host=/cloudsql/{db_instance_name}"
    else:
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
        int(os.getenv("MAX_FILE_SIZE_MB") or 10)
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

    is_production = bool(os.getenv("GOOGLE_CLOUD_PROJECT"))
    if not is_production:
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise RuntimeError(f"FALHA FATAL DE STARTUP: Faltam as seguintes variáveis "
                f"obrigatórias no seu .env local: {', '.join(missing)}"
            )
    
    if os.getenv("STORAGE_BACKEND") == "gcs":
        required_gcs = ["GCS_BUCKET_NAME"]
        if not is_production:
            required_gcs.append("GOOGLE_APPLICATION_CREDENTIALS")
        missing_gcs = [var for var in required_gcs if not os.getenv(var)]

        if missing_gcs:
            raise RuntimeError(
                f"FALHA FATAL DE STORAGE: O STORAGE_BACKEND está definido como 'gcs', "
                f"mas faltam as configurações da nuvem: {', '.join(missing_gcs)}"
            )
