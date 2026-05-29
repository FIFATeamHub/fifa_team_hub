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

**Decidido:** Flask (Python)

**Descartado:** FastAPI, Express.js

**Motivo:**  Escolhido pela simplicidade de configuração e abordagem amigável para o início dos estudos da equipe no ecossistema Python. 

### Banco de Dados & ORM:

**Decidido:** PostgreSQL

**Descartado:** MySQL, SQLite

**Motivo:**  Adotado por ser um banco relacional robusto e denso, aproveitando a familiaridade prévia do time com MySQL e SQLite. 


**Decidido:** SQLAlchemy + Alembic

**Descartado:** Prisma, Sequelize

**Motivo:**  Definido como ORM e ferramenta de migração oficial para integração nativa com o ecossistema Python/Flask. 

### Segurança & Autenticação

**Decidido:** Python-jose + jsonwebtoken

**Descartado:** passlib, bcrypt

**Motivo:**  Utilizados para implementar a estratégia de autenticação segura baseada em tokens JWT.

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

**Row-Level**
O uso de um sistema Row-Level (RLS) não foi abordado, porém, para o projeto, a tecnologia do RLS é essencial para garantir a segurança para evitar o vazamento de informações relevantes para adversários, pois garante restrições no acesso de uma linha de dados, como uma específica seleção e permitindo a com a equipe apenas para usúarios da comissão técnica ou o organizador do evento. O RLS atua diretamente em bancos de dados e limita a leitura de dados para usúarios específicos, sendo a perfeita alternativa na segurança do projeto.
---

## ADR-003 · Branches e Commits

### Branches

A estrutura de branches adotadas será:

- [ ] `main`➡ Principal branch do projeto.

- [ ] `SX_Y_branch` ➡ Branches utilizadas para as entregas das tasks. Sendo X a semana e Y o número da issue.

Exemplo: `S7_04_branch` ➡ Branch da Semana 7 para o Issue 04.


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



