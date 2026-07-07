---
title: "Semana 9 — Autenticação e Controle de Acesso"
description: JWT, bcrypt, middleware de rota, RBAC e pipeline CI/CD
---

import { Card, CardGrid } from '@astrojs/starlight/components'

# Semana 9 — Autenticação e Controle de Acesso

## Objetivo

Implementar o sistema de autenticação e controle de acesso — pilar de segurança do FIFA Team Hub. Sem autenticação robusta, o isolamento entre seleções não é garantido.

Esta semana também iniciou a **engenharia de requisitos formal** com documentação IEEE 830.

---

## Equipa desta Sprint

| Frente | Responsáveis |
|--------|-------------|
| **Backend** | Josef (Âncora) + Arthur (1ª vez BE real) |
| **Frontend** | Caio (Âncora) + João (1ª vez FE real) |
| **DevOps** | Júlia (Âncora) + Arthur |
| **Docs** | Arthur |

---

## Issues da Sprint

<CardGrid>
  <Card title="S9-01" icon="setting">
    **Modelo User + Migration Alembic**
    Campos: id (UUID), email (unique), password_hash, role (Enum), selection_id (FK), created_at
  </Card>
  <Card title="S9-02" icon="shield">
    **AuthService com bcrypt e JWT**
    hash_password(), verify_password(), create_access_token(), decode_token()
  </Card>
  <Card title="S9-03" icon="rocket">
    **Endpoints auth: /register, /login, /me**
    Validações, tratamento de erros, HTTP correto
  </Card>
  <Card title="S9-04" icon="approve-check">
    **Decorator @require_auth + @require_role**
    Extrai token, injeta g.current_user_id/role/selection_id
  </Card>
</CardGrid>

<CardGrid>
  <Card title="S9-05" icon="open-book">
    **Telas Login + Cadastro (Vue 3)**
    Pinia store, interceptors Axios, redirect por perfil
  </Card>
  <Card title="S9-06" icon="magnifier">
    **RBAC Frontend**
    usePermissions composable, PermissionGate component, página 403
  </Card>
  <Card title="S9-07" icon="cloud">
    **Variáveis JWT + GitHub Pages**
    .env.example, docker-compose, Pages configurado
  </Card>
  <Card title="S9-08" icon="github">
    **CI/CD GitHub Actions**
    Jobs: pytest (PostgreSQL) + ESLint + vue-tsc + Vitest
  </Card>
</CardGrid>

---

## Entregas Confirmadas

**Backend**
- ✅ Modelo User com UUID, email único, bcrypt hash
- ✅ JWT com payload: `{user_id, role, selection_id, exp}` (60 min)
- ✅ `POST /auth/register` → 201 | 409 (e-mail duplicado)
- ✅ `POST /auth/login` → JWT | 401 (sem revelar campo errado)
- ✅ `GET /auth/me` → dados do utilizador autenticado
- ✅ Decorator `@require_auth` e `@require_role()`
- ✅ AuditLog registado para LOGIN, LOGOUT, REGISTER

**Frontend**
- ✅ LoginPage e RegisterPage com validação client-side
- ✅ Token armazenado em localStorage após login
- ✅ `GET /auth/me` chamado automaticamente após login
- ✅ Redirect automático: /login se sem token, /dashboard se autenticado
- ✅ Interceptor Axios injetando `Authorization: Bearer <token>`
- ✅ Composable `usePermissions` + componente `<PermissionGate>`
- ✅ Página 403 para acesso negado

**DevOps / CI**
- ✅ `.github/workflows/ci.yml` com 2 jobs (backend + frontend)
- ✅ Trigger em PRs para `develop` e `main`
- ✅ Badge de CI no README
- ✅ GitHub Pages configurado (source: GitHub Actions)

**Documentação / Requisitos**
- ✅ 18 RFs, 10 RNFs, 6 REs (padrão IEEE 830)
- ✅ 18 User Stories com critérios BDD
- ✅ Diagramas UML (casos de uso + classes)
- ✅ Backlog com MoSCoW + MVP definido
- ✅ Collection Postman `docs/postman/s9_auth.json`

---

## Métricas

| Métrica | Meta | ✅ |
|---------|------|---|
| Issues concluídas | 13 | ✅ 13 |
| Endpoints funcionais | 3 | ✅ 3 |
| Telas FE | 2 | ✅ 2 |
| CI/CD jobs | 2 | ✅ 2 |
| Requisitos documentados | 34 | ✅ 34 |
| Testes de isolamento | 5+ | ✅ 5+ |
