# Guia de Deploy e Execução em Nuvem — FIFA Team Hub

Este guia descreve o processo de provisionamento, configuração e deploy contínuo do FIFA Team Hub no Google Cloud Platform (Cloud Run + Cloud SQL). A validação de PRs (testes/lint) roda via GitHub Actions (`ci.yml`); o deploy em si é feito por um **Cloud Build Trigger nativo do Google Cloud**, configurado para observar pushes na branch `main` do repositório.

---

## 1. 🛠️ Pré-requisitos

Antes de operar o deploy (manual ou via pipeline), garanta que você tem:

- **gcloud CLI** instalado e autenticado no projeto GCP correto:
  ```bash
  gcloud auth login
  gcloud config set project fifa-team-hub
  ```
- **Docker** instalado localmente (necessário para build/push manual das imagens de `backend/` e `frontend/`).
- **Acesso IAM ao projeto GCP `fifa-team-hub`**, com permissões mínimas para:
  - Cloud Run (`roles/run.admin`)
  - Cloud SQL (`roles/cloudsql.client` ou superior)
  - Artifact Registry (`roles/artifactregistry.writer`)
  - Secret Manager (`roles/secretmanager.secretAccessor` para leitura, `admin` para quem cria segredos)
- **Autenticação Docker no Artifact Registry** (necessária apenas para deploy manual):
  ```bash
  gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
  ```
- Acesso ao console do GCP (Cloud Build → Triggers) com permissão para configurar o Trigger de deploy, caso precise alterar sua configuração.

---

## 2. 🗄️ Provisionamento do Banco de Dados

O banco principal roda em **Cloud SQL para PostgreSQL 17** (mesma versão usada localmente via `docker-compose.yml` e no serviço de testes do CI).

Instância de produção referenciada pelos scripts e pelo `cloudbuild.yaml`: **`fifa-db-prod`**, na região **`us-central1`**.

Passos para provisionar (caso a instância ainda não exista):

```bash
gcloud sql instances create fifa-db-prod \
  --database-version=POSTGRES_17 \
  --region=us-central1 \
  --tier=db-custom-1-3840 \
  --storage-auto-increase

gcloud sql databases create fifa_team_hub --instance=fifa-db-prod

gcloud sql users create <DB_USER> \
  --instance=fifa-db-prod \
  --password=<DB_PASSWORD>
```

Pontos importantes:

- O Cloud Run se conecta à instância via **Cloud SQL Auth Proxy integrado**, usando a flag `--add-cloudsql-instances`. O nome de conexão segue o formato:
  ```
  <GCP_PROJECT_ID>:us-central1:fifa-db-prod
  ```
- Esse valor deve ser armazenado no Secret Manager como `CLOUD_SQL_INSTANCE_NAME` (usado pelo backend) e é passado ao Cloud Run pelo Cloud Build Trigger, via `cloudbuild.yaml`.
- A conta de serviço do backend (`fifa-team-hub-app@<PROJECT_ID>.iam.gserviceaccount.com`) precisa da role `roles/cloudsql.client` para conseguir abrir a conexão em runtime.
- A `DATABASE_URL` final deve apontar para o socket Unix do Cloud SQL quando rodando em Cloud Run, por exemplo:
  ```
  postgresql://<DB_USER>:<DB_PASSWORD>@/<DB_NAME>?host=/cloudsql/<CLOUD_SQL_INSTANCE_NAME>
  ```

> Em ambiente local, o banco sobe via `docker-compose.yml` (serviço `postgres`, imagem `postgres:17`), exposto na porta `15432`, sem necessidade de Cloud SQL.

---

## 3. 🔐 Variáveis de Ambiente e Segredos

O build e o deploy não dependem mais de secrets do GitHub: o Cloud Build Trigger roda inteiramente dentro do GCP, autenticado por uma Service Account do Cloud Build configurada no próprio console/`gcloud` (Cloud Build → Triggers), sem chaves estáticas nem federação de identidade com o GitHub. O único "cofre" relevante para a aplicação em runtime é o **Secret Manager (GCP)**, cujos segredos são injetados no Cloud Run via `--set-secrets` (ver `cloudbuild.yaml`, na raiz do repositório).

### Secret Manager / Ambiente do Cloud Run (injetados no backend via `--set-secrets`)

| Secret | Finalidade |
|---|---|
| `DATABASE_URL` | String de conexão completa com o PostgreSQL |
| `DB_PASSWORD` | Senha do usuário do banco |
| `DB_USER` | Usuário do banco |
| `DB_NAME` | Nome do banco de dados |
| `JWT_SECRET_KEY` | Chave para assinatura/validação dos tokens JWT |
| `SECRET_KEY` | Chave criptográfica de sessão da aplicação |
| `STORAGE_BACKEND` | Define o backend de armazenamento de arquivos (`gcs` em produção) |
| `GCS_BUCKET_NAME` | Nome do bucket do Cloud Storage usado para documentos |
| `GCP_PROJECT_ID` | ID do projeto GCP (também replicado como secret para uso em runtime) |
| `CLOUD_SQL_INSTANCE_NAME` | Connection name da instância Cloud SQL (`<PROJECT_ID>:us-central1:fifa-db-prod`) |

> **Nunca** commitar `.env` real ou credenciais no repositório. Localmente, use um `.env` (ignorado pelo Git) espelhando essas mesmas chaves; em produção, tudo deve vir do Secret Manager.

---

## 4. 🚀 Fluxo de Deploy

O deploy contínuo é feito por um **Cloud Build Trigger nativo do Google Cloud**, configurado para escutar pushes na branch `main` e executar automaticamente os steps definidos em **`cloudbuild.yaml`** (raiz do repositório):

1. **Build e push da imagem do backend** (`./backend`), tag `latest`.
2. **Migração do banco**: deploy e execução de um **Cloud Run Job** dedicado (`fifa-team-hub-migrate`), que roda `flask db upgrade` contra a instância Cloud SQL antes de qualquer coisa subir.
3. **Deploy do backend no Cloud Run** (`gcloud run deploy`):
   - conecta à instância Cloud SQL via `--add-cloudsql-instances`;
   - injeta os segredos de runtime via `--set-secrets` (tabela da seção 3);
   - roda com a service account de runtime configurada em `cloudbuild.yaml` (`_SERVICE_ACCOUNT`) e `--allow-unauthenticated`.
4. **Build e push da imagem do frontend** (`./frontend`), tag `latest`.
5. **Deploy do frontend no Cloud Run**, `--allow-unauthenticated`.

Antes de qualquer merge na `main`, o workflow **`.github/workflows/ci.yml`** já validou o PR:

- `backend-tests`: sobe um container `postgres:17` de teste e roda `pytest backend/tests/`.
- `frontend-lint`: roda `npm run lint` e `npm run type-check` no frontend.

### Deploy manual (fallback, via scripts locais)

Caso precise fazer deploy fora do pipeline, os scripts em `backend/scripts/` replicam a lógica do CD:

```bash
export DATABASE_URL=<sua-connection-string>
./backend/scripts/deploy-all.sh      # build + push + deploy de backend e frontend
# ou
./backend/scripts/deploy-cloud-run.sh   # apenas o backend
```

Esses scripts resolvem o `INSTANCE_CONN_NAME` dinamicamente via `gcloud sql instances describe fifa-db-prod` — exigem `gcloud` autenticado localmente.

---

## 5. 🔍 Troubleshooting (Erros Comuns)

| Sintoma | Causa provável | Ação |
|---|---|---|
| `Permission denied` / falha de autenticação na etapa de build ou deploy do Cloud Build Trigger | Service account do Cloud Build Trigger sem as roles necessárias (`roles/run.admin`, `roles/artifactregistry.writer`, `roles/iam.serviceAccountUser` na service account de runtime) | Revisar as roles da service account associada ao Trigger em Cloud Build → Configurações |
| `denied: Permission "artifactregistry.repositories.uploadArtifacts" denied` no push da imagem | Service account do Cloud Build Trigger sem role `roles/artifactregistry.writer` no repositório `fifa-team-hub` | Conceder a role na Artifact Registry para a service account do Trigger |
| Backend sobe no Cloud Run mas falha ao conectar no banco (erros de conexão/timeout no boot) | `CLOUD_SQL_INSTANCE_NAME` errado, instância não anexada via `--add-cloudsql-instances`, ou service account sem `roles/cloudsql.client` | Conferir o connection name (`gcloud sql instances describe fifa-db-prod`) e a role IAM da service account do runtime |
| Container falha no boot com erro de variável obrigatória ausente (`SECRET_KEY`, `DATABASE_URL`, `JWT_SECRET_KEY` etc.) | Segredo não existe no Secret Manager ou não foi incluído na flag `--set-secrets` do deploy | Criar o secret no Secret Manager (`gcloud secrets create ...`) e garantir que está listado em `cloudbuild.yaml` |
| CI falha em `backend-tests` mas passa localmente | Variáveis de ambiente de teste divergentes do `ci.yml` (ex.: `STORAGE_BACKEND=gcs` sem credenciais reais) | Rodar os testes localmente exportando exatamente as mesmas envs definidas no job `backend-tests` |
| Trigger não dispara após push na `main` | Cloud Build Trigger desabilitado ou configurado para observar outra branch/repositório | Conferir a configuração do Trigger em Cloud Build → Triggers no console do GCP |
| Upload de imagem lento ou falha por autenticação Docker (deploy manual) | `gcloud auth configure-docker` não foi executado para a região correta | Rodar `gcloud auth configure-docker us-central1-docker.pkg.dev --quiet` antes do `docker push` |
