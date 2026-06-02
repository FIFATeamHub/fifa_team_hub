# FIFA Team Hub

Sistema de gestão e auditoria para seleções nacionais, desenvolvido para centralizar documentação oficial, registros operacionais e processos administrativos utilizados por comissões técnicas, organizadores e auditores.

---

# Visão Geral

O FIFA Team Hub foi idealizado para resolver problemas de organização documental, rastreabilidade e isolamento de informações entre seleções nacionais durante competições e eventos oficiais.

A plataforma permitirá:

- Upload e gerenciamento de documentos oficiais
- Controle de acesso por seleção
- Auditoria completa de ações realizadas no sistema
- Centralização de dados operacionais
- Estrutura multi-tenant segura
- Organização de fluxos administrativos e técnicos

---

# Metodologia de Desenvolvimento

O projeto será desenvolvido utilizando:

| Metodologia | Aplicação |
|---|---|
| **Scrum** | Organização das sprints e gerenciamento das entregas |
| **Pair Programming** | Desenvolvimento colaborativo em rotação contínua |
| **Code Review** | Garantia de qualidade e padronização |
| **Git Flow** | Estratégia de versionamento e branches |

---

# Estrutura de Trabalho da Equipe

A equipe trabalhará em modelo colaborativo com rotação constante de pares durante o desenvolvimento.

Isso significa que:

- Não existirão papéis técnicos fixos para desenvolvimento
- Todos os membros poderão atuar em diferentes áreas do sistema
- O conhecimento será compartilhado continuamente
- A arquitetura será construída coletivamente

---

# Liderança Técnica

| Nome | Responsabilidade |
|---|---|
| Júlia Campos | Tech Lead · Arquitetura · DevOps · Organização Técnica |

---

## Equipe do Projeto

| Integrantes |
|---|
| Josef Woljtyla |
| João Sauma |
| Arthur Miguel |
| Caio Felipe |

---

# Atribuições Semanais

![Rotatividade dos Membros durante as semanas]("C:\Users\force\OneDrive\Imagens\rotatividade_dos_membros_fifa_team_hub.jpeg")

---

# Stack Tecnológica

A stack será definida e refinada ao longo das sprints iniciais conforme as necessidades do projeto.

## Tecnologias em avaliação

| Camada | Tecnologias |
|---|---|
| Frontend | Vue 3 |
| Backend | Flask |
| Banco de Dados e ORM | PostgreSQL · SQLAlchemy + Alembic |
| Segurança e Autenticação | Python-jose + jsonwebtoken |
| Infraestrutura | Docker · GitHub Actions |
| Storage | Google Cloud Storage |
| Deploy | A definir |

---

# Documentação do Projeto

A documentação oficial será mantida em um portal dedicado utilizando:

- Astro
- Markdown
- ADRs (Architecture Decision Records)

## Objetivos da documentação

- Centralizar decisões técnicas
- Documentar arquitetura
- Registrar aprendizados
- Facilitar onboarding
- Manter histórico técnico do projeto

---

# Como executar o programa com Docker

### 1. Clone o repositório:

```bash
git clone https://github.com/FIFATeamHub/fifa_team_hub.git
cd fifa-team-hub
```

### 2. Crie o arquivo `.env` na raiz do projeto com base no `.env.example`.

### 3. Execute o comando abaixo para construir e iniciar todos os serviços:

```bash
docker compose up --build
```

### 4. Após a inicialização:

   * PostgreSQL estará disponível na porta configurada no `docker-compose.yml`;
   * Backend estará disponível na porta `5000`;
   * Frontend estará disponível na porta `5173`.

### 5. Para interromper os serviços:

```bash
docker compose down
```

---

# Executando o projeto localmente (sem Docker)

## Pré-requisitos

  * Python 3.13+
  * Node.js 22+
  * PostgreSQL 15+
  * Git

### 1. Clone o repositório

```bash
git clone https://github.com/FIFATeamHub/fifa_team_hub.git
cd fifa-team-hub
```

### 2. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto utilizando o `.env.example` como referência.

### 3. Configure o banco de dados

Crie um banco PostgreSQL com as credenciais definidas no arquivo `.env`.

### 4. Inicie o backend

```bash
cd backend

python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt

python run.py
```

### 5. Inicie o frontend

Em outro terminal:

```bash
cd frontend

npm install

npm run dev
```

### 6. Acesse a aplicação

  * Frontend: http://localhost:5173
  * Backend: http://localhost:5000

---

# Estrutura Inicial do Repositório

```txt
fifa-team-hub/
├── backend/             # API e regras de negócio
├── frontend/            # Interface da aplicação
├── docs/                # Documentação técnica e ADRs
├── .github/             # Templates e CI/CD
└── README.md
