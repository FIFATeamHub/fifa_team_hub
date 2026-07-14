# Documento endpoints da autenticação

> **Nota:** a versão navegável e mais completa deste documento (com fluxo de aprovação e diagramas) está em [fifa-hub/api/auth](https://fifateamhub.github.io/fifa_team_hub/api/auth/), o site oficial de documentação.

## Endpoints

### Método POST (/auth/register):

- Descrição:
    Autocadastro **público**. Recebe os dados do visitante, valida as informações e verifica se o e-mail informado já existe no banco de dados. Em caso de sucesso, cria um novo registro de usuário com senha criptografada. O servidor **ignora qualquer `role`/`registration_status` enviado pelo cliente** — todo cadastro nasce `role=ATHELETE` e `registration_status=PENDING`, exigindo aprovação de um `AUDITOR` antes do primeiro login.
- Autenticação:
    Não Requerida
- Body (JSON):
    {email, password, full_name, selection_id}
- Respostas esperadas:
    201: { id, email, full_name, role, selection_id }
    400: { error: "..." } (campo obrigatório ausente, senha curta, e-mail inválido ou `selection_id` inexistente)
    409: { error: "Email já cadastrado" }


### Método POST (/auth/login):

- Descrição:
    Verifica as credenciais enviadas comparando-as com os registros do sistema. Bloqueia o login (`403`) se o cadastro ainda não estiver `APPROVED`. Em caso de sucesso, gera e retorna um token de acesso. Limitado a 5 tentativas por minuto por IP.
- Autenticação:
    Não Requerida
- Body (JSON):
    {email, password}
- Respostas esperadas:
    200: { access_token: "...", token_type: "bearer" }
    401: { error: "Credenciais inválidas" }
    403: { error: "Cadastro pendente de aprovação do Auditor" } | { error: "Cadastro rejeitado pelo Auditor" }
    429: limite de tentativas excedido


### Método POST (/auth/logout):

- Descrição:
    Requer token válido. Registra o evento de logout em auditoria. **Não invalida o token no servidor** — não há blacklist, o JWT permanece tecnicamente válido até expirar.
- Autenticação:
    Token obrigatório
- Respostas Esperadas:
    200: { message: "Logout realizado com sucesso" }


### Método GET (/auth/me):

- Descrição:
    Lê o token do usuário autenticado (header `Authorization: Bearer <token>`) e retorna o perfil correspondente.
- Autenticação:
    Token obrigatório
- Respostas Esperadas:
    200: { id, email, full_name, role, selection_id, is_active, created_at }
    401: { error: "Token não fornecido" } | { error: "Token inválido ou expirado" }

### Fluxo de aprovação de cadastro

Todo cadastro criado por `POST /auth/register` fica `PENDING` até que:
- um `AUDITOR` da mesma seleção aprove/rejeite via `POST /api/auth/registrations/<id>/approve` (body `{role}`) ou `POST /api/auth/registrations/<id>/reject`; ou
- no caso de concessão do papel `AUDITOR`, um `AUDITOR` só pode **indicar** (retorna `202`) e apenas um `ORGANIZER` pode **confirmar** a indicação via `GET /api/auth/registrations/pending` + `approve`.

### Criação de seleção (`/api/selection/`)

- `GET /api/selection/` — público, lista `{id, name, code}` de todas as seleções.
- `POST /api/selection/` — restrito a `ORGANIZER`. Cria uma seleção e seu primeiro `AUDITOR` (já `APPROVED`) atomicamente. Body: `{name, code, auditor_name, auditor_email, auditor_password}`.

### Payload do Token (JWT)

```json
{
  "sub": "uuid-do-usuario",
  "role": "TECHNICAL_STAFF",
  "selection_id": "uuid-ou-null",
  "exp": 1735689600
}
```

> A claim do id do usuário é `sub` (padrão JWT), não `user_id`.

## Uso do Token
Após o sucesso na autenticação (POST /auth/login), o frontend recebe o access_token e deve armazená-lo localmente de forma segura (geralmente em localStorage, sessionStorage ou cookies seguros).

Para aceder a qualquer rota protegida (como GET /auth/me), o frontend deve obrigatoriamente anexar este token em todas as requisições HTTP através do cabeçalho de autorização. O servidor intercepta a requisição através do decorador de segurança, lê o cabeçalho, decodifica o payload do JWT e valida se a assinatura matemática coincide com a chave secreta configurada no backend. A data e hora exatas do vencimento ficam gravadas dentro do próprio token, na propriedade exp. Como o token é assinado digitalmente pelo servidor, o utilizador não pode alterar esse tempo no lado do cliente.
