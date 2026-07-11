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
```

3. Adicionamos imediatamente a regra de bloqueio no arquivo `.gitignore`:

```
config/fifa-team-hub-key.json
```

## 5. Configuração do Ambiente de Desenvolvimento (Docker)

Para que a aplicação local consiga comunicar com a nuvem, o arquivo `.env` deve ser configurado com as variáveis mapeadas para o ambiente que o João irá integrar no Docker:

```bash
STORAGE_BACKEND=gcs
GCS_BUCKET_NAME=fifa-team-hub-documents
GCP_PROJECT_ID=fifa-team-hub
GOOGLE_APPLICATION_CREDENTIALS=/app/config/fifa-team-hub-key.json
```

No `docker-compose.yml`, o container do backend receberá estas variáveis e montará o volume de forma isolada e segura em modo "Apenas Leitura" (`:ro`):

```yaml
services:
  backend:
    build: ./backend
    environment:
      STORAGE_BACKEND: gcs
      GCS_BUCKET_NAME: fifa-team-hub-documents
      GCP_PROJECT_ID: fifa-team-hub
      GOOGLE_APPLICATION_CREDENTIALS: /app/config/fifa-team-hub-key.json
    volumes:
      - ./config/fifa-team-hub-key.json:/app/config/fifa-team-hub-key.json:ro
```

**Nota para Produção (Cloud Run):** O arquivo JSON é exclusivo para desenvolvimento local. Em produção no Cloud Run, utilizamos a identidade de serviço nativa (Workload Identity). Durante o deploy, associamos a conta de serviço `fifa-team-hub-app` ao container (através da flag `--service-account`), permitindo que a aplicação acesse o GCS de forma transparente sem a necessidade de chaves fixas, garantindo segurança máxima.

## 6. Script e Teste de Conectividade Real

Para validar se as permissões de IAM concedidas à Service Account estavam corretas, desenvolvemos um script de teste end-to-end (`config/test_gcs.py`).

Este script limpa variáveis residuais do sistema, inicializa o cliente oficial da Google apontando para a pasta local `config/` e executa um fluxo completo de gravação e leitura direta de objetos (ignorando restrições de leitura de metadados gerais de infraestrutura).

```python
import os
from google.cloud import storage

# Limpa resíduos de ambiente local
if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

print("--- TESTE DE INTEGRAÇÃO REAL (UPLOAD) ---")

try:
    # Inicializa o cliente apontando explicitamente para a nossa chave e projeto
    client = storage.Client.from_service_account_json(
        "config/fifa-team-hub-key.json",
        project="fifa-team-hub"
    )
    
    bucket = client.bucket("fifa-team-hub-documents")
    
    # Cria a referência de um arquivo temporário dentro do bucket
    blob = bucket.blob("testes_desenvolvimento/conexao.txt")
    
    print("Tentando fazer upload de um arquivo de teste...")
    blob.upload_from_string("Conexão do FIFA Team Hub realizada com sucesso!")
    print("✓ UPLOAD CONCLUÍDO!")
    
    print("Tentando ler o arquivo do bucket...")
    conteudo = blob.download_as_string()
    print(f"✓ DOWNLOAD CONCLUÍDO! Conteúdo: {conteudo.decode('utf-8')}")
    
    # Limpeza do bucket para não acumular lixo
    blob.delete()
    print("✓ Arquivo de teste removido do bucket.")

except FileNotFoundError:
    print("❌ ERRO: O arquivo não foi encontrado em 'config/fifa-team-hub-key.json'!")
except Exception as e:
    print(f"❌ Falha no teste: {e}")
```

**Resultado da Execução no Terminal:**

```
--- TESTE DE INTEGRAÇÃO REAL (UPLOAD) ---
Tentando fazer upload de um arquivo de teste...
✓ UPLOAD CONCLUÍDO!
Tentando ler o arquivo do bucket...
✓ DOWNLOAD CONCLUÍDO! Conteúdo: Conexão do FIFA Team Hub realizada com sucesso!
✓ Arquivo de teste removido do bucket.
```

Conclusão do Teste: O fluxo foi executado com sucesso absoluto. As permissões de escrita, leitura e eliminação de arquivos na nuvem estão totalmente operacionais, validando os critérios de aceitação da issue.