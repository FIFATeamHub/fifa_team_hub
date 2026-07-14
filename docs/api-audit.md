# API de Auditoria

> **Nota:** a versão navegável deste documento está em [fifa-hub/api/auditoria](https://fifateamhub.github.io/fifa_team_hub/api/auditoria/), o site oficial de documentação.

Endpoint exclusivo para leitura dos registros de auditoria e segurança do sistema. O acesso é restrito ao perfil `AUDITOR` e escopado pela sua própria seleção (visão global apenas se o auditor não estiver vinculado a nenhuma seleção). Nenhum endpoint de edição ou exclusão é disponibilizado por regra de negócio (imutabilidade).

### GET `/api/audit/`

Retorna de forma paginada e ordenada os logs de ações da plataforma.

**Parâmetros de Query String (Opcionais):**
- `page` *(int)*: Número da página atual. (Padrão: 1)
- `per_page` *(int)*: Quantidade de registros listados por página. (Padrão: 20)
- `action` *(string)*: Filtra por tipo de ação executada (ex: `LOGIN`, `UPLOAD`, `DELETE`, `REVIEW`, `ACCESS_DENIED`, `REGISTER_APPROVED`, `REGISTER_REJECTED`, `AUDITOR_NOMINATION_REQUESTED`, `AUDITOR_NOMINATION_REJECTED`).
- `user_id` *(uuid)*: Filtra apenas os logs gerados por um autor específico.
- `start_date` *(date, `YYYY-MM-DD`)*: Início do intervalo, interpretado em `America/Sao_Paulo` e convertido para UTC.
- `end_date` *(date, `YYYY-MM-DD`)*: Fim do intervalo, interpretado em `America/Sao_Paulo` e convertido para UTC.

**Regras de Segurança (RBAC):**
- Autenticação via token JWT é estritamente obrigatória (`401 Unauthorized`).
- Apenas usuários do grupo `AUDITOR` possuem permissão para consumir este recurso (`403 Forbidden`).

**Exemplo de Resposta de Sucesso:**
```json
{
  "data": [
    {
      "id": "abc-123",
      "action": "UPLOAD",
      "user_id": "xyz-987",
      "resource_id": "doc-555",
      "status": "SUCCESS",
      "ip_address": "192.168.1.1",
      "details": "Upload via painel",
      "created_at": "2026-07-09T18:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "pages": 8
  }
}
