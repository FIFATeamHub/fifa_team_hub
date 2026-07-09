# Manual de Execução e Deploy

Para subir o sistema do FIFA Team Hub em produção (Cloud Run, Docker, Servidor), as seguintes variáveis de ambiente são **estritamente obrigatórias**. A aplicação utiliza um mecanismo de *Fail Fast* e falhará imediatamente no boot se elas não existirem.

### Obrigatórias (Gerais):
- `SECRET_KEY`: Chave criptográfica de sessão usada internamente pelo Flask.
- `DATABASE_URL`: String de conexão com o banco de dados principal (PostgreSQL).
- `JWT_SECRET_KEY`: Chave criptográfica para geração e validação dos tokens JWT.

### Obrigatórias para Cloud Storage (se STORAGE_BACKEND=gcs):
- `GCS_BUCKET_NAME`: Nome do bucket reservado no Google Cloud Storage.
- `GOOGLE_APPLICATION_CREDENTIALS`: Caminho para o JSON de credenciais da conta de serviço (Service Account) do GCP.

> **Importante:** Jamais comite senhas ou o arquivo `.env` real neste repositório. Em produção, utilize o Secret Manager do Google Cloud para injetar essas variáveis de forma segura.

## Seções previstas

• Pré-requisitos

• Como rodar o projeto localmente

• Configuração do Deploy

• Variáveis de ambiente
