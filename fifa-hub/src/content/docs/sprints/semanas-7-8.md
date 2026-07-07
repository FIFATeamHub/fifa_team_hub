---
title: "Semanas 7 e 8 — Planejamento e Estrutura Inicial"
description: Formação da equipa, definição de stack, estrutura de repositório e setup inicial
---


import { Card, CardGrid } from '@astrojs/starlight/components'
import { defineConfig } from 'astro/config';
import remarkGfm from 'remark-gfm';

export default defineConfig({
  markdown: {
    remarkPlugins: [remarkGfm],
  },
});

# Semanas 7 e 8 — Planejamento e Estrutura Inicial

## Objetivo

As Semanas 7 e 8 foram dedicadas à organização inicial do **FIFA Team Hub**: definição da proposta, alinhamento da equipa, planejamento da arquitetura e configuração do ambiente.

---

## Semana 7 — Planejamento

### O que foi definido

<CardGrid>
  <Card title="🎯 Escopo" icon="document">
    Portal seguro de gestão de documentos para seleções nacionais, substituindo e-mails e drives manuais.
  </Card>
  <Card title="👥 Equipa" icon="users">
    5 membros com rotação semanal entre Backend, Frontend, DevOps e Docs.
  </Card>
  <Card title="🛠️ Stack" icon="setting">
    Vue 3 + Flask + PostgreSQL + GCS + Docker + GitHub Actions.
  </Card>
  <Card title="🗓️ Cronograma" icon="rocket">
    8 sprints (S7–S14), entregando funcionalidade real a cada semana.
  </Card>
</CardGrid>

### Stack Tecnológica Definida

| Camada | Tecnologia | Justificativa |
|--------|-----------|---------------|
| **Frontend** | Vue 3 + TypeScript | Menor curva de aprendizado para o time |
| **Backend** | Flask (Python 3.11) | Simplicidade de configuração |
| **ORM** | SQLAlchemy + Alembic | Integração nativa Python/Flask |
| **Banco** | PostgreSQL 15 | Robusto, familiar ao time |
| **Auth** | python-jose + bcrypt | JWT stateless seguro |
| **Storage** | Google Cloud Storage | Obrigatório pelos pré-requisitos do projeto |
| **Infra** | Docker + GitHub Actions | Ambientes reproduzíveis |

### Estrutura do Repositório

```
fifa_team_hub/
├── backend/           # Flask API (models, routes, services, middlewares)
├── frontend/          # Vue 3 + TypeScript (components, stores, composables)
├── fifa-hub/          # Esta documentação (Astro Starlight)
├── .github/workflows/ # CI/CD e deploy
├── docker-compose.yml
└── README.md
```

---

## Semana 8 — Estrutura Inicial

### Backend — Júlia (Âncora) + Josef

- ✅ Estrutura de pastas Flask com Factory Pattern e Blueprints
- ✅ `requirements.txt` com dependências iniciais
- ✅ `Dockerfile` com Python 3.11 e hot-reload
- ✅ Setup PostgreSQL via Docker Compose
- ✅ SQLAlchemy + Alembic inicializados
- ✅ Rota `GET /health → 200`
- ✅ Setup pytest com test fixtures

### Frontend — Caio (Âncora) + Arthur

- ✅ Vue 3 + TypeScript com Vite
- ✅ Pinia store inicializada
- ✅ Vue Router com rotas base (`/login`, `/dashboard`, `/404`)
- ✅ Componentes base: layout, formulário, tabela, toast, modal, spinner
- ✅ Axios configurado com `baseURL` e interceptors JWT
- ✅ Vitest + `@vue/test-utils` configurados

### DevOps — Júlia (Âncora) + João

- ✅ `docker-compose.yml` com PostgreSQL, Backend e Frontend
- ✅ `.env.example` com todas as variáveis necessárias
- ✅ `.gitignore` configurado (`.env`, `node_modules`, `__pycache__`)
- ✅ README com passos de setup (`docker compose up`)
- ✅ Todos rodando localmente

---

## Status ao Final da S8

| Área | Status |
|------|--------|
| Backend estruturado | ✅ |
| Frontend funcional | ✅ |
| Docker Compose operacional | ✅ |
| GitHub Pages estruturado | ✅ |
| CI/CD configurado | ✅ |
