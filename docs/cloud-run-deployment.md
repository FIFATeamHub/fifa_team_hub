# Deploy no Google Cloud Run

Este documento descreve como rodar o FIFA Team Hub localmente com armazenamento simulado (fake-gcs) e como fazer o deploy em produção no Google Cloud Run com armazenamento real no Google Cloud Storage (GCS).

## Visão geral

A aplicação suporta dois backends de armazenamento de documentos, controlados pela variável de ambiente `STORAGE_BACKEND`:

- `local`: salva arquivos no disco local (útil para rodar sem depender de nenhum serviço de storage).
- `gcs`: salva arquivos no Google Cloud Storage. Em desenvolvimento, isso é simulado pelo [`fake-gcs-server`](https://github.com/fsouza/fake-gcs-server); em produção, aponta para um bucket real do GCS.

## Ambiente de desenvolvimento local

### Pré-requisitos

- Docker e Docker Compose instalados
- Arquivo `.env` na raiz do projeto, preenchido a partir de `.env.example`

### Subindo o ambiente

```bash
docker-compose up -d --build
```

Isso sobe 5 serviços:

| Serviço | Porta | Descrição |
|---|---|---|
| `backend` | 5000 | API Flask |
| `frontend` | 5173 | Interface web (Vite) |
| `postgres` | 15432 → 5432 | Banco de dados |
| `fake-gcs` | 4443 | Simulador do Google Cloud Storage |
| `gcs-init` | — | Serviço one-shot que cria o bucket no `fake-gcs` antes do backend subir |

### Aplicando as migrations

Na primeira subida (ou sempre que o volume do Postgres for recriado):

```bash
docker-compose exec backend flask db upgrade
```

### Criando o bucket no fake-gcs

O `fake-gcs-server` não vem com nenhum bucket pré-criado. O `docker-compose.yml` já cuida disso automaticamente: o serviço `gcs-init` espera o `fake-gcs` responder e cria o bucket `fifa-team-hub-documents` antes do `backend` subir (`depends_on: gcs-init: condition: service_completed_successfully`). Não é preciso nenhum passo manual em `docker-compose up`.

Se precisar recriar o bucket manualmente (por exemplo, depois de mexer nos dados do fake-gcs), o script continua disponível e é idempotente — rodar de novo não dá erro se o bucket já existir:

```bash
docker-compose exec backend bash scripts/setup-fake-gcs.sh
```

Esse script:
1. Espera o `fake-gcs` responder antes de tentar criar o bucket.
2. Cria o bucket `fifa-team-hub-documents` via API JSON do GCS (`POST /storage/v1/b`) apenas se ele ainda não existir.
3. Lista os buckets existentes para confirmar a criação.

> **Nota técnica**: o `fake-gcs-server` expõe a mesma API JSON do GCS real (`/storage/v1/b/...`), não uma API simplificada. Chamadas como `PUT /{bucket}` (formato de acesso direto a objetos) retornam 404 — o formato correto de criação de bucket é `POST /storage/v1/b?project={project_id}` com o nome no corpo da requisição.

> **Nota sobre rede**: o serviço `gcs-init` (e o script, quando rodado dentro do `backend`) se conecta ao fake-gcs pelo nome do serviço Docker (`http://fake-gcs:4443`), não por `localhost`. Containers na mesma rede Docker se enxergam pelo nome do serviço, não pelo host da máquina.

### Verificando que tudo subiu corretamente

```bash
docker-compose ps
docker-compose logs backend --tail=50
curl http://localhost:5000/health
```

O endpoint `/health` deve retornar HTTP 200.

## Variáveis de ambiente

| Variável | Onde é usada | Exemplo (dev) | Exemplo (produção) |
|---|---|---|---|
| `STORAGE_BACKEND` | backend | `gcs` | `gcs` |
| `GCS_BUCKET_NAME` | backend | `fifa-team-hub-documents` | `fifa-team-hub-documents` |
| `GCP_PROJECT_ID` | backend | `test-project` | ID real do projeto GCP |
| `STORAGE_EMULATOR_HOST` | backend, fake-gcs | `http://fake-gcs:4443` | *(não definida)* |
| `DATABASE_URL` | backend | `postgresql://user:pass@postgres:5432/db` | string de conexão do Cloud SQL |
| `JWT_SECRET_KEY` | backend | valor de dev | segredo gerenciado (ex: Secret Manager) |
| `JWT_EXPIRE_MINUTES` | backend | `30` | conforme necessidade |

> Importante: `STORAGE_EMULATOR_HOST` só deve existir em desenvolvimento. Em produção, sua ausência faz com que o client do Google Cloud Storage se conecte automaticamente ao serviço real (`storage.googleapis.com`), autenticando via a Service Account do Cloud Run.

## Deploy em produção (Cloud Run)

### Dockerfile

O `Dockerfile` do backend é otimizado para Cloud Run:
- Usa `gunicorn` como servidor WSGI de produção (não o servidor de desenvolvimento do Flask).
- Escuta na porta definida por `$PORT` (Cloud Run injeta `PORT=8080` por padrão).
- Possui um `HEALTHCHECK` que consulta `/health`.

### Script de deploy

```bash
bash backend/scripts/deploy-cloud-run.sh
```

O script:
1. Builda a imagem Docker do backend.
2. Envia (`push`) a imagem para o Google Container Registry (`gcr.io`).
3. Faz o deploy no Cloud Run via `gcloud run deploy`, configurando:
   - Variáveis de ambiente de storage (`STORAGE_BACKEND`, `GCS_BUCKET_NAME`, `GCP_PROJECT_ID`)
   - Service Account dedicada (`fifa-team-hub-app@{PROJECT_ID}.iam.gserviceaccount.com`)
   - Escalonamento automático: mínimo de 1 instância, máximo de 10
   - Timeout de 60s e 512Mi de memória por instância

> Antes de rodar, ajuste `PROJECT_ID` no início do script para o ID real do projeto no Google Cloud. IDs de projeto GCP só aceitam letras minúsculas, números e hífen (não aceitam `_`).

### Pré-requisitos para o deploy

- `gcloud` CLI autenticado (`gcloud auth login`) e configurado com o projeto correto (`gcloud config set project SEU_PROJETO`)
- Permissão de push no Container Registry do projeto
- Bucket real do GCS já criado (`gsutil mb gs://fifa-team-hub-documents`)
- Service Account `fifa-team-hub-app` criada, com permissão de leitura/escrita no bucket (papel `roles/storage.objectAdmin` ou equivalente)

### Kubernetes / manifesto alternativo

Um manifesto de Deployment Kubernetes equivalente está disponível em `k8s/deployment.yaml`, para cenários que usem GKE em vez de Cloud Run gerenciado. Ele inclui:
- 2 réplicas
- Liveness probe em `/health`
- Limites de recursos (256Mi/250m de request, 512Mi/500m de limit)

## Troubleshooting

Problemas comuns encontrados durante o desenvolvimento deste ambiente, e suas causas:

| Sintoma | Causa provável |
|---|---|
| `password authentication failed` ao conectar no Postgres | O volume do Postgres já existia de uma subida anterior com credenciais diferentes. O Postgres só aplica `POSTGRES_USER`/`POSTGRES_PASSWORD` na primeira inicialização de um volume vazio. Resolva com `docker-compose down -v` e suba de novo. |
| `curl: command not found` dentro do container backend | A imagem `python:3.13-slim` não inclui `curl` por padrão; precisa ser instalado explicitamente no Dockerfile via `apt-get install curl`. |
| `Client sent an HTTP request to an HTTPS server` ao chamar o fake-gcs | O `fake-gcs-server` serve HTTPS por padrão. É necessário passar `command: ["-scheme", "http"]` no serviço `fake-gcs` do `docker-compose.yml` para aceitar conexões HTTP puras. |
| `scripts/setup-fake-gcs.sh: line 1: #!/bin/bash: No such file or directory` | O arquivo `.sh` foi salvo com um BOM (Byte Order Mark) UTF-8, comum em editores no Windows. Salve o arquivo como UTF-8 **sem BOM**. |
| `$'\r': command not found` ao rodar um script `.sh` | O arquivo tem quebras de linha estilo Windows (CRLF) em vez de Unix (LF). Um `.gitattributes` com `*.sh text eol=lf` na raiz do repositório previne esse problema para todo o time. |
| `curl: (7) Failed to connect to localhost port 4443` dentro do container backend | Dentro de um container, `localhost` refere-se ao próprio container, não a outros serviços do Docker Compose. Use o nome do serviço (`fake-gcs`) em vez de `localhost` para comunicação entre containers. |
