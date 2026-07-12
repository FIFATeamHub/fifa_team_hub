# Guia de Deploy e Execução em Nuvem — FIFA Team Hub

Este guia descreve o processo de provisionamento, configuração e deploy contínuo do FIFA Team Hub no Google Cloud Platform (Cloud Run + Cloud SQL), com CI/CD via GitHub Actions.

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
- Acesso ao repositório GitHub com permissão para configurar **Secrets** (Settings → Secrets and variables → Actions), caso precise alterar credenciais do pipeline de CD.

---

## 2. 🗄️ Provisionamento do Banco de Dados

O banco principal roda em **Cloud SQL para PostgreSQL 17** (mesma versão usada localmente via `docker-compose.yml` e no serviço de testes do CI).

Instância de produção referenciada pelos scripts e pelo workflow de CD: **`fifa-db-prod`**, na região **`us-central1`**.

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
- Esse valor deve ser armazenado no Secret Manager como `CLOUD_SQL_INSTANCE_NAME` (usado pelo backend) e é passado ao Cloud Run pelo workflow de CD.
- A conta de serviço do backend (`fifa-team-hub-app@<PROJECT_ID>.iam.gserviceaccount.com`) precisa da role `roles/cloudsql.client` para conseguir abrir a conexão em runtime.
- A `DATABASE_URL` final deve apontar para o socket Unix do Cloud SQL quando rodando em Cloud Run, por exemplo:
  ```
  postgresql://<DB_USER>:<DB_PASSWORD>@/<DB_NAME>?host=/cloudsql/<CLOUD_SQL_INSTANCE_NAME>
  ```

> Em ambiente local, o banco sobe via `docker-compose.yml` (serviço `postgres`, imagem `postgres:17`), exposto na porta `15432`, sem necessidade de Cloud SQL.

---

## 3. 🔐 Variáveis de Ambiente e Segredos

Existem dois "cofres" distintos que **não devem ser confundidos**:

- **GitHub Secrets** → usados apenas pelo pipeline de CI/CD para autenticar no GCP e fazer o build/push/deploy.
- **Secret Manager (GCP)** → segredos injetados diretamente no runtime do Cloud Run via `--update-secrets`, consumidos pela aplicação.

### GitHub Secrets (pipeline `cd.yml`)

| Secret | Finalidade |
|---|---|
| `WIF_PROVIDER` | Identity Provider do Workload Identity Federation, usado para autenticação sem chave estática (`google-github-actions/auth@v2`) |
| `GCP_SERVICE_ACCOUNT` | E-mail da service account impersonada pelo GitHub Actions para publicar imagens e fazer deploy |
| `GCP_PROJECT_ID` | ID do projeto GCP (`fifa-team-hub`), usado para compor URLs de imagem e nome da instância Cloud SQL |

### Secret Manager / Ambiente do Cloud Run (injetados no backend via `--update-secrets`)

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

O deploy contínuo é feito pelo workflow **`.github/workflows/cd.yml`**, disparado em dois cenários:

1. **Push direto na branch `main`** (merge de PR já validado pelo `ci.yml`).
2. **Disparo manual** via `workflow_dispatch` (aba *Actions* → CD → *Run workflow*).

Passo a passo executado pelo pipeline:

1. **Checkout** do código.
2. **Autenticação no GCP via WIF** (`google-github-actions/auth@v2`), usando `WIF_PROVIDER` + `GCP_SERVICE_ACCOUNT` — sem chaves JSON estáticas.
3. **Setup do Cloud SDK** e `gcloud auth configure-docker` para o Artifact Registry (`us-central1-docker.pkg.dev`).
4. **Build e push da imagem do backend** (`./backend`), tag `<sha do commit>`.
5. **Build e push da imagem do frontend** (`./frontend`), tag `<sha do commit>`.
6. **Deploy do backend no Cloud Run** (`google-github-actions/deploy-cloudrun@v2`):
   - conecta à instância Cloud SQL via `--add-cloudsql-instances`;
   - injeta os segredos de runtime via `--update-secrets` (tabela da seção 3);
   - roda com a service account `GCP_SERVICE_ACCOUNT` e `--allow-unauthenticated`.
7. **Deploy do frontend no Cloud Run**, mesma service account, `--allow-unauthenticated`.

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
| `Permission denied` / `unable to impersonate` na etapa de autenticação do CD | `WIF_PROVIDER` ou `GCP_SERVICE_ACCOUNT` incorretos, ou a service account não tem `roles/iam.workloadIdentityUser` vinculada ao pool do GitHub | Revisar o Workload Identity Pool no GCP e o binding IAM entre o repositório e a service account |
| `denied: Permission "artifactregistry.repositories.uploadArtifacts" denied` no push da imagem | Service account do CD sem role `roles/artifactregistry.writer` no repositório `fifa-team-hub` | Conceder a role na Artifact Registry para a `GCP_SERVICE_ACCOUNT` |
| Backend sobe no Cloud Run mas falha ao conectar no banco (erros de conexão/timeout no boot) | `CLOUD_SQL_INSTANCE_NAME` errado, instância não anexada via `--add-cloudsql-instances`, ou service account sem `roles/cloudsql.client` | Conferir o connection name (`gcloud sql instances describe fifa-db-prod`) e a role IAM da service account do runtime |
| Container falha no boot com erro de variável obrigatória ausente (`SECRET_KEY`, `DATABASE_URL`, `JWT_SECRET_KEY` etc.) | Segredo não existe no Secret Manager ou não foi incluído na flag `--update-secrets` do deploy | Criar o secret no Secret Manager (`gcloud secrets create ...`) e garantir que está listado na etapa de deploy do `cd.yml` |
| CI falha em `backend-tests` mas passa localmente | Variáveis de ambiente de teste divergentes do `ci.yml` (ex.: `JWT_ALGORITHM`, `STORAGE_BACKEND=gcs` sem credenciais reais) | Rodar os testes localmente exportando exatamente as mesmas envs definidas no job `backend-tests` |
| `workflow_dispatch` não aparece na aba Actions | Workflow `cd.yml` não está na branch padrão (`main`) ainda | Garantir que o arquivo já foi mesclado na `main`; o GitHub só lista gatilhos manuais de workflows presentes na branch padrão |
| Upload de imagem lento ou falha por autenticação Docker (deploy manual) | `gcloud auth configure-docker` não foi executado para a região correta | Rodar `gcloud auth configure-docker us-central1-docker.pkg.dev --quiet` antes do `docker push` |
