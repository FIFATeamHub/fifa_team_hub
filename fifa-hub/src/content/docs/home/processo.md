---
title: Processo de Desenvolvimento
description: Metodologia, rituais e padrões de qualidade do projeto FIFA Team Hub
---

import { Card, CardGrid } from '@astrojs/starlight/components'

# Processo de Desenvolvimento

O FIFA Team Hub segue uma metodologia ágil adaptada ao contexto acadêmico, com sprints semanais, rotação de papéis e foco em qualidade desde o início.

---

## Rituais da Equipe

<CardGrid>
  <Card title="📅 Reunião Semanal" icon="pencil">
    **Toda quinta-feira** via Discord.
    Revisão do que foi feito, planejamento da próxima sprint e alinhamento técnico.
  </Card>
  <Card title="⏰ Prazo de Issues" icon="rocket">
    **Sábado até 12h.**
    Todas as issues da sprint devem estar concluídas e com PR aberto até este horário.
  </Card>
  <Card title="🔀 Code Review" icon="approve-check">
    **PR obrigatório com 1 aprovação.**
    Nenhum código sobe para `develop` ou `main` sem revisão de pares.
  </Card>
  <Card title="🔄 Rotação de Papéis" icon="refresh">
    **A cada sprint**, membros rodam entre Backend, Frontend, DevOps e Docs para aprendizado distribuído.
  </Card>
</CardGrid>

---

## Fluxo de Trabalho Git

```
main          ← Protegida. Apenas via PR aprovado + CI passando.
develop       ← Integração. Merge de features aprovadas.
feature/*     ← Desenvolvimento. Uma branch por issue.
```

**Padrão de commits:** Conventional Commits

```
feat: adicionar endpoint de upload de documentos
fix: corrigir validação de MIME type
docs: documentar endpoints de autenticação
chore: atualizar dependências do backend
test: adicionar testes de isolamento cross-selection
```

**Nomenclatura de branches:**
```
feature/s10-be-upload
feature/s10-fe-listagem
feature/s11-do-gcs
docs/s9-auth-documentation
```

---

## Política de PRs

1. Branch criada a partir de `develop`
2. Issue associada ao PR
3. CI/CD deve passar (testes + lint + type-check)
4. Mínimo 1 aprovação de outro membro
5. **PRs com conflito são negados diretamente** *(definido em 18/06)*
6. **Variáveis em inglês e minúsculo** *(padrão definido em 18/06)*
7. Merge squash para manter histórico limpo

---

## Pipeline CI/CD

Cada PR dispara automaticamente:

```yaml
jobs:
  backend-tests:
    - pytest (com PostgreSQL service container)
    - flake8 (linting)
    - cobertura mínima: 60%

  frontend-lint-type-tests:
    - ESLint
    - vue-tsc (type-check)
    - Vitest
```

**Falha = bloqueio de merge.** Não existe exceção.

---

## Padrões de Qualidade

| Área | Padrão |
|------|--------|
| **Testes BE** | pytest, coverage ≥ 60%, testes de isolamento obrigatórios |
| **Testes FE** | Vitest + @vue/test-utils, jsdom |
| **Linting BE** | flake8 / ruff sem erros |
| **Linting FE** | ESLint sem warnings |
| **Tipagem FE** | TypeScript strict mode, vue-tsc clean |
| **Segurança** | Testes cross-selection bloqueadores em CI |
| **Auditoria** | 100% dos eventos registados em AuditLog |

---

## Estrutura do Repositório

```
fifa_team_hub/
├── .github/
│   ├── workflows/          # CI/CD e deploy
│   └── ISSUE_TEMPLATE/
├── backend/
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── routes/         # Blueprints e endpoints
│   │   ├── services/       # Lógica de negócio (StorageService, AuthService)
│   │   └── middlewares/    # @require_auth, @require_role
│   ├── tests/              # pytest
│   └── migrations/         # Alembic
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── stores/         # Pinia
│   │   └── composables/
│   └── tests/              # Vitest
├── fifa-hub/               # Esta documentação (Astro Starlight)
├── docker-compose.yml
└── README.md
```
