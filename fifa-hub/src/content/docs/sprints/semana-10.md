---
title: "Semana 10 — Upload e Listagem"
description: Endpoint de upload multipart, listagem filtrada por seleção, componentes Vue e testes de isolamento
---

import { Card, CardGrid } from '@astrojs/starlight/components'

# Semana 10 — Upload e Listagem

## Objetivo

Implementar o **core funcional do FIFA Team Hub**: upload de documentos com validações de segurança no servidor, armazenamento em disco local (preparado para GCS na S11) e listagem filtrada por seleção com isolamento garantido.

---

## Equipa desta Sprint

| Frente | Responsáveis |
|--------|-------------|
| **Backend** | Arthur (Âncora) + Caio (1ª vez BE real) |
| **Frontend** | João (Âncora) + Josef (1ª vez FE real) |
| **DevOps** | Júlia (Âncora) + João |
| **Docs** | Caio |

---

## Issues da Sprint

<CardGrid>
  <Card title="S10-BE-01" icon="document">
    **Endpoint POST /documents/upload**
    Validação MIME (python-magic), max 10 MB, doc_type Enum, selection_id do token
  </Card>
  <Card title="S10-BE-02" icon="magnifier">
    **GET /documents com filtro por seleção**
    TECHNICAL_STAFF: apenas sua seleção. ORGANIZER: CONVOCACAO + PASSAPORTE. Paginação.
  </Card>
  <Card title="S10-BE-03" icon="close">
    **DELETE /documents/{id} (soft delete)**
    Apenas autor pode excluir. deleted_at no banco. Ficheiro físico removido.
  </Card>
  <Card title="S10-FE-01" icon="up-caret">
    **UploadDocumentModal.vue**
    Barra de progresso (onUploadProgress), validação client-side, feedback 413/415/403
  </Card>
</CardGrid>

<CardGrid>
  <Card title="S10-FE-02" icon="list-format">
    **DocumentList.vue**
    Badges de status, filtros por tipo, paginação, skeleton loader, RBAC por perfil
  </Card>
  <Card title="S10-DO-01" icon="setting">
    **Storage local + variáveis de ambiente**
    Volume Docker, StorageService abstract (prep para GCS), STORAGE_BACKEND=local
  </Card>
  <Card title="S10-DC-01" icon="open-book">
    **Documentação dos endpoints**
    api-documents.md, modelo Document, regras de validação, Postman collection
  </Card>
  <Card title="S10-QA-01" icon="shield">
    **Testes de isolamento (bloqueadores)**
    5+ cenários cross-selection. Falha bloqueia merge no CI.
  </Card>
</CardGrid>

---

## Entregas Confirmadas

**Arthur Miguel**
> Implementou o endpoint DELETE de documentos com soft delete.

**João Sauma**
> Implementou a listagem de documentos com filtro no frontend.

**Caio Felipe**
> Implementou upload de documentos, GET /documents, GET /documents/{id} e AuditLog.

**Backend**
- ✅ Modelo Document com SQLAlchemy (id, selection_id, uploaded_by, doc_type, original_name, stored_name, file_size_kb, mime_type, status, created_at, deleted_at)
- ✅ Migration Alembic aplicada
- ✅ `POST /documents/upload` com validação de MIME type (python-magic)
- ✅ `GET /documents` com filtro por selection_id + paginação
- ✅ `DELETE /documents/{id}` com soft delete e remoção do ficheiro físico
- ✅ `selection_id` preenchido automaticamente do token (nunca do body)
- ✅ AuditLog para UPLOAD, DELETE, ACCESS_DENIED

**Frontend**
- ✅ Componente `UploadDocumentModal.vue` com barra de progresso
- ✅ Composable `useDocuments.ts`
- ✅ Componente `DocumentList.vue` com badges PENDENTE/APROVADO/REJEITADO
- ✅ Filtros por tipo de documento + paginação
- ✅ Ação eliminar com diálogo de confirmação (TECHNICAL_STAFF)
- ✅ Vista diferenciada ORGANIZER (sem botão eliminar, coluna "Seleção")

**DevOps**
- ✅ Pasta `backend/storage/uploads/` com `.gitkeep`
- ✅ Volume Docker montado (uploads persistem após `docker compose down/up`)
- ✅ `StorageService` abstract + `LocalStorageService`
- ✅ Interface pronta para migração para GCS

**Decisões tomadas na retrospectiva (18/06):**
- ⚠️ PRs com conflito serão negados diretamente
- ⚠️ Padronizar variáveis para inglês e minúsculo

---

## Métricas

| Métrica | Meta | ✅ |
|---------|------|---|
| Issues concluídas | 8 | ✅ 8 |
| Endpoints BE | 3 (upload, listagem, delete) | ✅ 3 |
| Telas FE | 2 (modal + listagem) | ✅ 2 |
| Testes de isolamento | 8+ cenários | ✅ 8+ |
| Storage preparado para GCS | ✅ | ✅ |
