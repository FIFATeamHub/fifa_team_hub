---
title: "Semana 11 — Cloud Storage (GCS)"
description: Migração de storage local para Google Cloud Storage, links assinados e preparação para Cloud Run
---

import { Card, CardGrid } from '@astrojs/starlight/components'

# Semana 11 — Storage e Persistência: Google Cloud Storage

## Objetivo

Sprint mais técnica do projeto até aqui. Migrar o armazenamento de ficheiros de disco local para o **Google Cloud Storage**, implementar links temporários assinados e preparar o ambiente para deploy em Cloud Run.

---

## Equipa desta Sprint

| Frente | Responsáveis | Destaque |
|--------|-------------|---------|
| **Backend** | Caio (Âncora) + Júlia (1ª vez BE real) | Júlia integra BE com GCS |
| **Frontend** | Josef (Âncora) + Arthur (2ª vez FE) | Arthur aprofunda FE |
| **DevOps** | Arthur (Protagonista) + João (Âncora) | Arthur lidera Cloud (faz o curso!) |
| **Docs** | João (Responsável) | Documenta enquanto configura |

---

## Issues da Sprint

<CardGrid>
  <Card title="S11-BE-01 🔴 CRÍTICA" icon="setting">
    **Implementar GCSStorageService**
    Interface abstract → LocalStorageService → GCSStorageService. Factory por STORAGE_BACKEND.
  </Card>
  <Card title="S11-BE-02 🟠 ALTA" icon="shield">
    **Links Temporários Assinados (Download)**
    GET /documents/{id}/download → URL assinada GCS válida 15 min. 410 se expirada.
  </Card>
  <Card title="S11-DO-01 🔴 CRÍTICA (BLOQUEANTE)" icon="cloud">
    **Bucket GCS + Service Account**
    Criar bucket, configurar permissões, gerar chave JSON, documentar setup.
  </Card>
  <Card title="S11-DO-02 🟡 MÉDIA" icon="rocket">
    **Docker + Cloud Run Preparation**
    Dockerfile otimizado (gunicorn, PORT=8080), fake-gcs local, scripts deploy.
  </Card>
</CardGrid>

<CardGrid>
  <Card title="S11-FE-01 🟡 MÉDIA" icon="document">
    **Frontend adaptado para URLs GCS**
    getDownloadUrl() no composable, botão "Baixar" com link assinado, preview.
  </Card>
  <Card title="S11-QA-01 🟠 ALTA" icon="magnifier">
    **Testes de Isolamento com GCS**
    5+ cenários cross-selection com mock GCS. Testes de edge case (quota, blob not found).
  </Card>
</CardGrid>

---

## Ordem de Execução

| Prioridade | Issue | Motivo |
|-----------|-------|--------|
| 1️⃣ **BLOQUEANTE** | S11-DO-01 | Nada funciona sem bucket + credenciais |
| 2️⃣ **CRÍTICA** | S11-BE-01 | Desbloqueia todas as outras |
| 3️⃣ **ALTA** | S11-BE-02 | Links assinados para download |
| 4️⃣ **ALTA** | S11-QA-01 | Testes bloqueadores de CI |
| 5️⃣ **MÉDIA** | S11-FE-01 | Ajuste de UI (após BE-02) |
| 6️⃣ **MÉDIA** | S11-DO-02 | Preparação para S13 (pode ser paralela) |

---

## Decisões Técnicas

**StorageService com Factory Pattern:**
```python
def get_storage_service() -> StorageService:
    backend = os.getenv("STORAGE_BACKEND", "local")
    if backend == "gcs":
        return GCSStorageService(bucket_name=..., project_id=...)
    else:
        return LocalStorageService(local_path=...)
```

**Links assinados com expiração de 15 minutos:**
```python
url = blob.generate_signed_url(
    version="v4",
    expiration=timedelta(minutes=15),
    method="GET"
)
```

**Variáveis de Ambiente Adicionadas:**
```env
STORAGE_BACKEND=gcs
GCS_BUCKET_NAME=fifa-team-hub-documents
GCP_PROJECT_ID=seu-projeto-gcp
GOOGLE_APPLICATION_CREDENTIALS=/app/config/key.json
```

---

## Sucesso da Sprint = ✅

1. S11-DO-01 entregue (bucket acessível)
2. S11-BE-01 + S11-BE-02 PRs aprovados
3. S11-QA-01 bloqueador ativo no CI
4. S11-FE-01 funcional (download com URLs assinadas)
5. S11-DO-02 pronto para S13
6. Nenhum documento acessível via URL direta (sempre assinada)
7. Isolamento entre seleções 100% em testes
