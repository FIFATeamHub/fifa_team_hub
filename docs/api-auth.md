# Documento endpoints da autenticação

## Endpoints

### Método POST (/auth/login):
<!-- async function login(credenciais) {
    const resposta = await fetch(`${apiUrl}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(credenciais)
    }) -->
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
    