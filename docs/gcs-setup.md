# Configuração do Google Cloud Storage (GCS) - FIFA Team Hub

Este documento descreve o passo a passo para configurar a infraestrutura de armazenamento em nuvem no Google Cloud Platform (GCP) utilizada na Sprint S11 para substituir o armazenamento local.

---

## 1. Criação do Bucket no Google Cloud Storage

O bucket funciona como o nosso "disco virtual" na nuvem, onde serão centralizados os documentos das seleções (convocações, exames médicos e contratos).

1. Acesse o [Console do Google Cloud](https://console.cloud.google.com/).
2. No seletor de projetos (topo da página), certifique-se de estar no projeto correto ou crie um novo com o ID exatamente igual a `fifa-team-hub`.
3. No menu lateral esquerdo, navegue até **Cloud Storage** > **Buckets**.
4. Clique em **+ Criar** (Create).
5. Configure o bucket com os seguintes parâmetros:
   * **Nome do bucket:** `fifa-team-hub-documents` (O nome deve ser globalmente único).
   * **Tipo de local:** Escolha **Region** e selecione `southamerica-east1`.
   * **Classe de armazenamento:** Escolha **Standard** (ideal para arquivos acessados frequentemente).
   * **Controle de acesso:** Escolha **Uniforme** (Uniform) para centralizar a gestão de permissões via IAM.
6. Clique em **Criar**.

---

## 2. Criação da Service Account (Conta de Serviço)

A Service Account é a identidade técnica (um "robô") que o nosso backend em Python/Flask usará para se autenticar no Google Cloud de forma automatizada, sem expor contas pessoais.

1. No menu lateral esquerdo, vá em **IAM e administrador** (IAM & Admin) > **Contas de serviço** (Service Accounts).
2. Clique em **+ Criar conta de serviço** (+ Create Service Account) no topo da tela.
3. No campo **Nome da conta de serviço**, digite: `fifa-team-hub-app`.
4. Clique em **Criar e continuar**.
5. Na etapa de concessão de acesso, clique em **Selecionar um papel** (Select a role) e escolha:
   * **Administrador de objetos do Storage** (`Storage Object Admin`).
   * *Nota:* Esta role garante permissões totais de leitura, escrita e exclusão de objetos dentro do bucket.
6. Clique em **Continuar** e depois em **Concluir** (Done).

---

## 3. Geração da Chave JSON de Autenticação

1. Na listagem de Contas de Serviço, clique sobre o e-mail da conta recém-criada (`fifa-team-hub-app@...`).
2. Vá até a aba **Chaves** (Keys) na parte superior.
3. Clique em **Adicionar chave** (Add Key) > **Criar nova chave** (Create new key).
4. Certifique-se de que o formato **JSON** está selecionado e clique em **Criar**.
5. O download do arquivo de credenciais será feito automaticamente pelo navegador.

---

## 4. Estrutura Local e Segurança (Desenvolvimento)

O arquivo JSON baixado contém credenciais críticas e **nunca** deve ser enviado para o sistema de controle de versão.

1. Renomeie o arquivo baixado para `fifa-team-hub-key.json`.
2. Mova o arquivo para a pasta `config/` na raiz do projeto:
   ```text
   fifa-team-hub/
   ├── config/
   │   └── fifa-team-hub-key.json