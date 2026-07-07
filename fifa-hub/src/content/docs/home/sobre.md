---
title: Sobre o Projeto
description: FIFA Team Hub — Portal seguro de gestão de documentos para seleções nacionais
---

# FIFA Team Hub

**Portal seguro de gestão de documentos para comissões técnicas de seleções nacionais de futebol.**

Desenvolvido no programa **AILAB Makers Fase 2** (Sprints 7–14), o projeto substitui processos manuais por um portal auditável com isolamento absoluto entre seleções.

---

## O Problema

Comissões técnicas de seleções nacionais gerenciam documentos críticos — convocações, passaportes, laudos médicos, relatórios táticos — através de e-mails, drives compartilhadas e planilhas. Isso gera:

- ❌ Risco de vazamento de informações entre seleções
- ❌ Falta de rastreabilidade (quem acessou o quê e quando)
- ❌ Conflitos de versão e documentos desatualizados
- ❌ Sem conformidade com LGPD

## A Solução

<CardGrid>
  <Card title="🔐 Isolamento Inviolável" icon="shield">
    Row-level filtering obrigatório em todas as queries. Tecnicamente impossível acessar dados de outra seleção.
  </Card>
  <Card title="📁 Gestão Centralizada" icon="document">
    Upload de convocações, passaportes, laudos médicos e relatórios táticos num portal único.
  </Card>
  <Card title="🔍 Auditoria Completa" icon="magnifier">
    Logs imutáveis de LOGIN, UPLOAD, DOWNLOAD, DELETE com timestamp, IP e responsável.
  </Card>
  <Card title="☁️ Cloud Nativo" icon="cloud">
    Armazenamento no Google Cloud Storage com links temporários assinados (15 min).
  </Card>
</CardGrid>

---

## Stack Tecnológica

| Camada | Tecnologia |
|--------|------------|
| **Frontend** | Vue 3 + TypeScript + Pinia |
| **Backend** | Flask (Python 3.11) + Blueprint Pattern |
| **ORM / Migrations** | SQLAlchemy + Alembic |
| **Banco de Dados** | PostgreSQL 15 |
| **Autenticação** | python-jose (JWT) + bcrypt |
| **Storage** | Google Cloud Storage |
| **Deploy** | Google Cloud Run + Docker |
| **CI/CD** | GitHub Actions |
| **Documentação** | Astro Starlight + GitHub Pages |

---

## Perfis de Acesso

| Perfil | Acesso |
|--------|--------|
| **TECHNICAL_STAFF** | Upload e listagem dos documentos da própria seleção |
| **ORGANIZER** | Visualização de CONVOCACAO e PASSAPORTE de todas as seleções |
| **AUDITOR** | Painel de logs e auditoria de eventos |

---

## Repositório

**GitHub:** [FIFATeamHub/fifa_team_hub](https://github.com/FIFATeamHub/fifa_team_hub)

**Documentação:** [fifateamhub.github.io/fifa_team_hub](https://fifateamhub.github.io/fifa_team_hub/)
