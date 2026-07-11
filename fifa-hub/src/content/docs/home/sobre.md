---
title: Visão Geral do Projeto
description: FIFA Team Hub — Portal seguro de gestão de documentos para seleções nacionais
---

import { Card, CardGrid } from '@astrojs/starlight/components'

# FIFA Team Hub

**Portal seguro de gestão de documentos para comissões técnicas de seleções nacionais de futebol.**

Desenvolvido no programa **AILAB Makers — Fase 2** (Sprints 7–14), o projeto substitui processos manuais por um portal auditável com isolamento entre seleções, implantado em produção no Google Cloud.

---

## O Problema

Comissões técnicas de seleções nacionais gerenciam documentos críticos — convocações, passaportes, laudos médicos, relatórios táticos — através de e-mails, drives compartilhadas e planilhas. Isso gera:

- Risco de vazamento de informações entre seleções
- Falta de rastreabilidade (quem acessou o quê e quando)
- Conflitos de versão e documentos desatualizados
- Ausência de um histórico auditável para conformidade com a LGPD

## A Solução

<CardGrid>
  <Card title="Isolamento por Seleção" icon="shield">
    Toda consulta, upload e exclusão é filtrada pela seleção do usuário autenticado. Tentativas de acesso cruzado são bloqueadas e registradas.
  </Card>
  <Card title="Gestão Centralizada" icon="document">
    Upload de convocações, passaportes, laudos médicos, relatórios táticos e esquemas de jogadas num portal único.
  </Card>
  <Card title="Auditoria Completa" icon="magnifier">
    Logs imutáveis de LOGIN, LOGOUT, UPLOAD, DOWNLOAD, DELETE e ACCESS_DENIED, com timestamp, IP e responsável.
  </Card>
  <Card title="Cloud Nativo" icon="cloud">
    Armazenamento no Google Cloud Storage com links de download temporários e assinados (15 min), backend e frontend publicados no Cloud Run.
  </Card>
</CardGrid>

---

## Stack Tecnológica

| Camada | Tecnologia |
|--------|------------|
| **Frontend** | Vue 3 + Vite + Pinia |
| **Backend** | Flask 3 (Python 3.11), organizado em routes → controllers → services |
| **ORM / Migrations** | SQLAlchemy + Alembic |
| **Banco de Dados** | PostgreSQL 17 (Cloud SQL em produção) |
| **Autenticação** | JWT (python-jose) + hash de senha via Werkzeug |
| **Storage** | Google Cloud Storage, com abstração local para desenvolvimento |
| **Deploy** | Docker + Google Cloud Run, imagens publicadas no Google Container Registry |
| **CI** | GitHub Actions (testes de backend e lint/type-check de frontend em cada PR) |
| **Documentação** | Astro Starlight + GitHub Pages |

## Perfis de Acesso

| Perfil | Acesso |
|--------|--------|
| **ATHELETE** | Upload e leitura do próprio passaporte e laudo médico, dentro da própria seleção |
| **TECHNICAL_STAFF** | Upload e listagem de convocações, relatórios táticos e esquemas de jogadas da própria seleção |
| **MEDICAL_STAFF** | Upload e leitura de laudos médicos da própria seleção |
| **ORGANIZER** | Leitura de convocações e passaportes de todas as seleções |
| **AUDITOR** | Consulta ao painel de logs de auditoria da própria seleção |

---

## Repositório

**GitHub:** [FIFATeamHub/fifa_team_hub](https://github.com/FIFATeamHub/fifa_team_hub)

**Documentação:** [fifateamhub.github.io/fifa_team_hub](https://fifateamhub.github.io/fifa_team_hub/)
