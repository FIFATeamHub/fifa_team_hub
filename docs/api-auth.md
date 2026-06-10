# Documento endpoints da autenticação

## Endpoints

### Método POST (/auth/register):
<!-- async function register(dadosUsuario) {
    const resposta = await fetch(`${apiUrl}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(dadosUsuario)
    })
} -->
- Descrição:    
    Recebe os dados do visitante, valida as informações e verifica se o e-mail informado já existe no banco de dados. Em caso de sucesso, cria um novo registro de usuário com senha criptografada.
- Autenticação:
    Não Requerida
- Body (JSON):
    {email, password, role, selection_id}
- Respostas esperadas:
    201: { id, email, role } 
    400: { error: { email: ["..."], password: ["..."] } }
    409: { error: "Email já cadastrado" }


### Método POST (/auth/login):
<!-- async function login(credenciais) {
    const resposta = await fetch(`${apiUrl}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(credenciais)
    })
} -->
- Descrição:    
    Verifica as credenciais enviadas comparando-as com os registros do sistema. Em caso de sucesso, gera e retorna um token de acesso.
- Autenticação:
    Não Requerida
- Body (JSON):
    {email, senha}
- Respostas esperadas:
    200: { access_token: "...", token_type: "bearer" } 
    401: { error: "Credenciais inválidas" }


### Método GET (/auth/me):
<!-- async function fetchMe() {
const res = await fetch(`${apiUrl}/auth/me`, {
  headers: {
    Authorization: `Bearer ${token.value}`,
  },
})} -->

- Descrição:
A omissão do método GET dentro do código, indica ao fetch sua presença de imediato
Na parte do cabeçalho (headers: Authorization) indica que o método GET irá ler o token do usuário e retornar o perfil do próprio
- Autenticação:
    Token obrigatório
- Respostas Esperadas:
    200: { id, email, role, selection_id }
    401: { error: "Token não fornecido" } | { error: "Token inválido ou expirado" }

### Payload do Token (JWT)

{
  "user_id": "uuid",
  "role": "TECHNICAL_STAFF",
  "selection_id": "uuid-ou-null",
  "exp": 1735689600
}

## Uso do Token
Após o sucesso na autenticação (POST /auth/login), o frontend recebe o access_token e deve armazená-lo localmente de forma segura (geralmente em localStorage, sessionStorage ou cookies seguros).

Para aceder a qualquer rota protegida (como GET /auth/me), o frontend deve obrigatoriamente anexar este token em todas as requisições HTTP através do cabeçalho de autorização. O servidor intercepta a requisição através do decorador de segurança, lê o cabeçalho, decodifica o payload do JWT e valida se a assinatura matemática coincide com a chave secreta configurada no backend. A data e hora exatas do vencimento ficam gravadas dentro do próprio token, na propriedade exp. Como o token é assinado digitalmente pelo servidor, o utilizador não pode alterar esse tempo no lado do cliente