# Decisões técnicas (ADR)

Documento vivo — atualizar sempre que uma decisão relevante for tomada em reunião.

---

## ADR-001 · Stacks escolhidas

### Frontend:

**Decidido:** Vue 3

**Descartado:** React + Vite

**Motivo:** Escolhido devido ao menor tempo de curva de aprendizado necessário para o time aplicar em um projeto de tiro curto. 


**Decidido:** CSS Puro

**Descartado:** Tailwind CSS

**Motivo:**  Adotado para estilização para simplificar o desenvolvimento e otimizar o tempo, evitando a introdução de frameworks de estilização complexos neste momento. 

### Backend:

**Decidido:** Flask (Python) `v3.1.x`

**Descartado:** FastAPI, Express.js

**Motivo:**  Escolhido pela simplicidade de configuração e abordagem amigável para o início dos estudos da equipe no ecossistema Python.

### Banco de Dados & ORM:

**Decidido:** PostgreSQL `v17`

**Descartado:** MySQL, SQLite

**Motivo:**  Adotado por ser um banco relacional robusto e denso, aproveitando a familiaridade prévia do time com MySQL e SQLite.


**Decidido:** SQLAlchemy + Alembic

**Descartado:** Prisma, Sequelize

**Motivo:**  Definido como ORM e ferramenta de migração oficial para integração nativa com o ecossistema Python/Flask. 

### Segurança & Autenticação

**Decidido:** python-jose[cryptography] (JWT) + Werkzeug (Hash)

**Descartado:** jsonwebtoken (específico de Node.js)

**Motivo:** A biblioteca `python-jose` garante o uso correto da especificação JWT com o algoritmo HS256 no backend Python. Já a ferramenta embutida `werkzeug.security` (via `generate_password_hash`) foi escolhida para as senhas pois dispensa a instalação de libs pesadas adicionais como bcrypt ou passlib.

### Infraestrutura & Storage

**Decidido:** Google Cloud Storage

**Descartado:** MinIO

**Motivo:**  Definido como obrigatório pelos pré-requisitos gerais do projeto para o armazenamento seguro de arquivos.

---

## ADR-002 · Isolamentos e Regras de Acesso

- Um usuário comum não pode pertencer a mais de uma seleção.

- A Comissão Técnica possui acesso restrito exclusivamente aos documentos da sua própria seleção (Multitenancy).
 
- O Organizador do campeonato possui visão global e irrestrita sobre todas as seleções.

 **Gestão de Documentos (Upload/Delete):**

- O Atleta é o responsável por realizar o upload inicial dos arquivos (Passaporte, Laudos, Exames, etc). 

- Formatos de arquivos aceitos estritamente limitados a .pdf e .jpg. 

- A exclusão de um documento só pode ser efetuada pelo Organizador ou pelo próprio Atleta que realizou o upload. 

- Fluxo de Laudos Médicos: Estados definidos para o ciclo de vida do documento: Pendente ➡ Aprovado ou Rejeitado. 

**Regra de Validação de Inscrição:** 
Uma seleção só será considerada "Confirmada" para o Organizador quando todos os documentos obrigatórios de todos os membros forem devidamente enviados no sistema. 

**Row-Level:**
O uso de um sistema Row-Level (RLS) não foi abordado, porém, no projeto, a tecnologia do RLS é essencial para garantir a segurança para evitar o vazamento de informações relevantes para adversários, pois garante restrições no acesso de uma linha de dados, como uma específica seleção, e permite a visualização da equipe apenas para usúarios da comissão técnica ou o organizador do evento. O RLS atua diretamente em bancos de dados e limita a leitura de dados para usúarios específicos, sendo a perfeita alternativa na segurança do projeto.

---

## ADR-003 · Branches e Commits

### Branches

A estrutura de branches adotadas será:

- [ ] `main`➡ Principal branch do projeto.

- [ ] `SX_Y_branch` ➡ Branches utilizadas para as entregas das tasks. Sendo X a semana e Y o número da issue.

Exemplo: `S7_04_branch` ➡ Branch da Semana 7 para o Issue 04.

## ADR-004: Exclusão de Documentos (Soft Delete + Hard Storage Delete)
**Contexto**: Precisamos definir como a exclusão de documentos se comportará para respeitar as exigências de auditoria e otimização de nuvem.
**Decisão**: O registro no banco de dados sofrerá *Soft Delete* (`status="DELETED"` e preenchimento de `deleted_at`) para compor trilhas de auditoria, garantindo a integridade referencial. Contudo, os arquivos físicos vinculados serão apagados do Storage (GCS/Local) para economizar custos.


### Commits

**Tipos de alteração**

- [ ] `feat`: Nova funcionalidade
- [ ] `fix`: Correção de bug
- [ ] `docs`: Alteração em documentação
- [ ] `refactor`: Melhoria/limpeza de código (sem alterar comportamento)
- [ ] `test`: Adição ou modificação de testes
- [ ] `chore`: Atualização de dependências ou tarefas burocráticas

Exemplo de mensagem no commit:
"feat: adicionando X função"
"docs: adicionando informação no decisoes.md"

## ADR-005: Logout (sem Blacklist de Token)

**Contexto**: Precisávamos de um endpoint de logout que ao menos deixasse rastro de auditoria (`LogAction.LOGOUT`) do encerramento de sessão.

**Decisão**: Por ora, `POST /auth/logout` apenas registra o `AuditLog` de sucesso e retorna 200 — o JWT em si **não é invalidado** no backend (ele continua tecnicamente válido até expirar). A invalidação real, via blacklist/revogação de token (ex.: tabela de tokens revogados ou Redis com TTL), fica como **melhoria futura (follow-up)**, fora do escopo desta sprint para economizar tempo/tokens.

---

## Débito técnico conhecido

Uma varredura completa da documentação (14/07/2026) identificou um conjunto de arquivos órfãos e desvios de versão entre ambientes. A lista completa, com justificativa de cada item, está em [Changelog — Débito técnico conhecido](https://fifateamhub.github.io/fifa_team_hub/changelog/) no site oficial. Nenhum desses itens foi removido nesta rodada — ficam registrados para um PR de limpeza dedicado.



## ADR-006 · Auditoria de Downloads

### Decisão

A auditoria de downloads registra a geração da URL assinada, e não o download efetivo do arquivo.

### Justificativa

Os documentos são disponibilizados por meio de URLs assinadas. Após a geração da URL, o download ocorre diretamente no serviço de armazenamento, sem retornar ao backend. Dessa forma, o backend consegue auditar de forma confiável quem solicitou acesso ao documento, mesmo não sendo possível confirmar se o arquivo foi efetivamente baixado.