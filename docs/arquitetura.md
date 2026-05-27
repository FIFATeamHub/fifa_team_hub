# Arquitetura e modelagem de dados

## Entidades principais (A refinar em equipe)

• **User:** Representa os usuários do sistema (Technical Staff, Organizer, Auditor).

• **Selection:** Representa a seleção nacional (ex: Brasil, Argentina).

• **Document:** Arquivos submetidos (Passaportes, Laudos, etc).

• **AuditLog:** Registro imutável de ações no sistema.

---

## Regra de isolamento (Multi-tenant)

Todo acesso deve ser isolado pela seleção de origem do usuário logado. Nenhuma rota deve retornar documentos de outras seleções acidentalmente.
