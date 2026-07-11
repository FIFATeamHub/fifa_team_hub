# Documentação da API — Módulo de Documentos (Sprint 10)

Esta especificação serve como referência oficial para o desenvolvimento do Frontend e auditoria do sistema. Todos os endpoints abaixo exigem autenticação via JWT Bearer Token.

---

## 🏗️ Modelo de Dados (Document)

O modelo representa os metadados dos arquivos persistidos no sistema.

<br>

### Campos do Modelo
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | UUID | Identificador único e exclusivo gerado automaticamente (v4). |
| `selection_id` | UUID | Identificador da seleção associada ao usuário ou documento. |
| `uploaded_by` | UUID | ID do usuário que realizou o upload. |
| `original_name` | String | Nome original do arquivo higienizado via `secure_filename`. |
| `storage_url` | String | Caminho interno e seguro do armazenamento do arquivo. |
| `type` | Enum | Categoria/tipo do documento (ver Enums abaixo). |
| `status` | Enum | Estado de aprovação do documento (ver Enums abaixo). |
| `created_at` | DateTime | Carimbo de data/hora completo gerado no fuso horário `America/Sao_Paulo`. |

<br>

### Enums Utilizados

#### 1. `TypeDocument` (Tipos de Documento)
* `CONVOCADO`
* `PASSPORT`
* `LAUDO_MEDICO`
* `RELATORIO_TATICO`


#### 2. `DocStatus` (Estados do Documento)
* `PENDING`: Documento aguardando revisão.
* `APPROVED`: Documento aprovado e ativo.

---

## 🛡️ Regras Globais de Validação de Arquivos

Antes de qualquer persistência ou validação de permissão por perfil, o arquivo físico enviado passa por uma camada de segurança rigorosa baseada no arquivo `document.py`:

1.  **Limite de Tamanho:** Máximo de **10 MB** (`10 * 1024 * 1024` bytes).
2.  **Validação Real de Natureza (MIME Type):** Para mitigar ataques de extensão falsa, a validação lê os primeiros 2048 bytes usando a biblioteca `python-magic`.
3.  **MIME Types Aceitos:**
    * `application/pdf` (Documentos PDF)
    * `image/jpeg` (Imagens JPEG)
    * `image/png` (Imagens PNG)
    * `application/vnd.openxmlformats-officedocument.wordprocessingml.document` (Arquivos Word `.docx`)

---

## 🗺️ Endpoints da API

<br>

### 1. Criar/Upload de Documento
* **Endpoint:** `POST /document/upload`
* **Content-Type:** `multipart/form-data`
* **Autenticação:** Obrigatória (Bearer Token)

<br>

#### Matriz de Permissão e Comportamento por Perfil (`validate_upload_permission`):
| Perfil (Role) | Tipo de Documento Permitido | Status Inicial no Banco |
| :--- | :--- | :--- |
| **AUDITOR** | `PASSPORT` | `APPROVED` |
| **TECHNICAL_STAFF** | `CONVOCADO`, `RELATORIO_TATICO` <br> `PASSPORT` | `APPROVED` <br> `PENDING` |
| **MEDICAL_STAFF** | `LAUDO_MEDICO` <br> `PASSPORT` | `APPROVED` <br> `PENDING` |
| **ATHELETE** | `PASSPORT`, `LAUDO_MEDICO` | `PENDING` |

<br>

#### Parâmetros do Body (Multipart)
* `file` (arquivo binário, obrigatório): O arquivo a ser carregado.
* `doc_type` (string, obrigatório): O valor correspondente a um dos Enums de `TypeDocument`.

<br>

#### Respostas Possíveis

##### 🟢 201 Created
Documento e log de auditoria salvos com sucesso.
```json
{
  "id": "a90f23db-2eb3-4ef1-8931-df2914ba1962",
  "original_name": "passaporte_caio.png",
  "doc_type": "PASSPORT",
  "file_size_kb": 1240,
  "status": "PENDING",
  "uploaded_by": "53e24cf8-df12-421c-ba92-f02a392bb123",
  "created_at": "2026-06-20T10:15:30-03:00"
}
```

##### 🔴 400 Bad Request (Ausência de Parâmetros)
```json
{
  "error": "Nenhum arquivo enviado no campo 'file' "
}
```

<br>

```json
{
  "error": "O campo 'doc_type' é obrigatório"
}
```


##### 🔴 403 Forbidden (Perfil Sem Permissão)

```json
{
  "error": "Acesso negado.",
  "details": "Acesso negado. O perfil 'ATHELETE' não tem permissão para fazer upload de 'RELATORIO_TATICO'."
}
```

##### 🔴 413 Payload Too Large (Tamanho Excedido)

```json
{
  "error": "Arquivo muito grande. O limite máximo é 10 MB",
  "status_code": 413
}
```

##### 🔴 415 Unsupported Media Type (MIME Tipo Inválido)

```json
{
  "error": "Tipo de mídia 'text/plain' não permitido. Envie PDF, JPEG ou PNG.",
  "status_code": 415
}
```


##### 🔴 500 Internal Server Error
```json
{
  "error": "Erro interno ao salvar arquivo",
  "details": "Descrição detalhada da exceção do banco de dados."
}
```

<br>

---

<br>

### 2. Listar Documentos Acessíveis

<br>

* **Endpoint:** `GET /document`
* **Método HTTP:** `GET`
* **Autenticação:** Obrigatória (Bearer Token)

<br>

#### Parâmetros de Query (URL)
| Parâmetro | Tipo | Obrigatório | Padrão | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `type` | String | Sim | N/A | Filtra a listagem por um tipo específico do enum `TypeDocument` (ex: `RELATORIO_TATICO`). |
| `page` | Inteiro | Não | `1` | Define o número da página atual para fins de paginação do banco. |
| `per_page` | Inteiro | Não | `10` | Define o limite máximo de registros exibidos por página. |

<br>


#### Matriz de Permissão e Visibilidade de Escopo (`list_accessible_documents`):
| Perfil (Role) | Tipos de Documento Visíveis | Escopo / Restrição de Acesso |
| :--- | :--- | :--- |
| **ORGANIZER** | `PASSPORT`, `CONVOCADO` | **Global:** Pode visualizar os documentos de todas as seleções existentes no sistema. |
| **AUDITOR** | `PASSPORT`, `LAUDO_MEDICO` | **Local:** Limitado estritamente aos jogadores pertencentes à sua própria seleção (`selection_id`). |
| **TECHNICAL_STAFF** | `CONVOCADO`, `LAUDO_MEDICO`, `RELATORIO_TATICO`, `ESQUEMA_JOGADAS` <br><br> `PASSPORT` | **Misto:** <br>• Apenas documentos coletivos da sua própria seleção (`selection_id`). <br>• Para passaportes, possui direito de leitura **apenas sobre o seu próprio arquivo** (`user_id`). |
| **MEDICAL_STAFF** | `LAUDO_MEDICO` <br><br> `PASSPORT` | **Misto:** <br>• Apenas laudos médicos da sua própria seleção (`selection_id`). <br>• Para passaportes, possui direito de leitura **apenas sobre o seu próprio arquivo** (`user_id`). |
| **ATHLETE** | `CONVOCADO`, `LAUDO_MEDICO`, `RELATORIO_TATICO`, `ESQUEMA_JOGADAS` <br><br> `PASSPORT` | **Misto:** <br>• Visualiza arquivos coletivos/táticos da sua própria seleção (`selection_id`). <br>• Para passaportes, possui direito de leitura **apenas sobre o seu próprio arquivo** (`user_id`). |

<br>

#### Respostas Possíveis


##### 🟢 200 OK (Listagem Processada com Sucesso)
Retorna uma estrutura padronizada contendo a lista higienizada de metadados (`data`) e os metadados auxiliares de navegação da página (`pagination`).
```json
{
  "data": [
    {
      "id": "a90f23db-2eb3-4ef1-8931-df2914ba1962",
      "original_name": "passaporte_caio.png",
      "doc_type": "PASSPORT",
      "storage_url": "backend/storage/uploads/53e24cf8/a90f23db.png",
      "status": "PENDING",
      "uploaded_by_id": "53e24cf8-df12-421c-ba92-f02a392bb123",
      "selection_id": "90b14cd2-fa32-411a-8212-e88dfba44111",
      "created_at": "2026-06-20T10:15:30-03:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 1,
    "pages": 1
  }
}
```

##### 🔴 403 Forbidden
```json
{
  "error": "Acesso negado. Perfil inválido."
}
```

##### 🔴 500 Internal Server Error (Instabilidade no Banco)
```json
{
  "error": "Erro interno ao processar a consulta de documentos.",
  "details": "Exceção disparada pela camada do SQLAlchemy durante a execução do paginate."
}
```

<br>

---

<br>

### 3. Obter Detalhes de um Documento por ID
* **Endpoint:** `GET /document/{document_id}`
* **Método HTTP:** `GET`
* **Autenticação:** Obrigatória (Bearer Token)

<br>

#### Parâmetros de Path (URL)
| Parâmetro | Tipo | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- |
| `document_id` | UUID | Sim | O identificador único e exclusivo do documento cadastrado no banco de dados. |

<br>


#### Matriz de Permissão e Detalhes de Escopo (`get_accessible_document`):
| Perfil (Role) | Tipos de Documento Permitidos para Leitura | Regra de Restrição Adicional por Registro |
| :--- | :--- | :--- |
| **ORGANIZER** | `PASSPORT`, `CONVOCADO` | **Acesso Global:** Pode acessar os registros de qualquer seleção do sistema. |
| **AUDITOR** | `PASSPORT`, `LAUDO_MEDICO` | **Acesso Regional:** Limitado estritamente aos membros da sua seleção (`selection_id`). |
| **TECHNICAL_STAFF** | `CONVOCADO`, `LAUDO_MEDICO`, `RELATORIO_TATICO`, `ESQUEMA_JOGADAS` <br><br> `PASSPORT` | **Acesso Misto:** <br>• Arquivos de estratégia coletivos da seleção são liberados. <br>• Passaportes só são visíveis se o arquivo pertencer ao seu próprio ID (`document.user_id == user_id`). |
| **MEDICAL_STAFF** | `LAUDO_MEDICO` <br><br> `PASSPORT` | **Acesso Misto:** <br>• Prontuários e laudos da sua própria seleção são liberados. <br>• Passaportes só são visíveis se o arquivo pertencer ao seu próprio ID (`document.user_id == user_id`). |
| **ATHLETE** | `CONVOCADO`, `LAUDO_MEDICO`, `RELATORIO_TATICO`, `ESQUEMA_JOGADAS` <br><br> `PASSPORT` | **Acesso Misto:** <br>• Arquivos coletivos liberados para a sua respectiva equipe. <br>• Passaportes só são visíveis se o arquivo pertencer ao seu próprio ID (`document.user_id == user_id`). |

<br>

#### Comportamento de Auditoria de Segurança
Caso um usuário tente realizar uma invasão de escopo (ex: tentar ler o passaporte de outro membro ou acessar arquivos de outra seleção), a requisição falha na validação de segurança e executa de forma transacional a chamada automática do `register_audit_log` salvando um registro crítico contendo a ação `LogAction.ACCESS_DENIED`, o status de `"FAILURE"` e o motivo real detalhado do bloqueio.

<br>

#### Respostas Possíveis

##### 🟢 200 OK (Metadados do Documento Higienizados)
Retorna os metadados do documento com sucesso. O campo `storage_url` é omitido intencionalmente neste endpoint para proteção e integridade do arquivo físico.
```json
{
  "id": "a90f23db-2eb3-4ef1-8931-df2914ba1962",
  "original_name": "passaporte_caio.png",
  "doc_type": "PASSPORT",
  "status": "PENDING",
  "selection_id": "90b14cd2-fa32-411a-8212-e88dfba44111",
  "created_at": "2026-06-20T10:15:30-03:00"
}
```

##### 🔴 403 Forbidden (Bloqueio por Invasão de Escopo ou Quebra de Regra)

```json
{
  "error": "Acesso negado."
}
```

##### 🔴 404 Not Found (Documento Inexistente)

```json
{
  "error": "Documento não encontrado."
}
```

##### 🔴 500 Internal Server Error (Falha Operacional Crítica)

```json
{
  "error": "Erro interno ao buscar metadados do documento.",
  "details": "Mensagem detalhada do erro gerado pela conexão com a tabela."
}
```



## 📝 Decisões de Arquitetura e Auditoria

### Rastreamento de Logs de Download (`LogAction.DOWNLOAD`)

* **Contexto**: O enum `LogAction.DOWNLOAD` foi mapeado no ecossistema da aplicação para auditar o fluxo de consumo de arquivos pelas delegações técnicas e organizadores da FIFA.
* **Decisão de Escopo**: O evento de auditoria será registrado de forma síncrona no exato momento em que a URL assinada (*Signed URL*) do Google Cloud Storage for gerada com sucesso pelo backend através do endpoint `/document/<id>/download`.
* **Justificativa Técnica**: Rastrear o download definitivo (o momento exato em que o cliente baixa os bytes do bucket do GCS) exigiria a implementação de webhooks, microsserviços de mensageria ou *callbacks* adicionais de infraestrutura em nuvem, o que foi classificado como fora de escopo para os objetivos e prazos da sprint atual.
* **Mitigação de Ambiguidades**: Para garantir total transparência e clareza para o **AUDITOR** do sistema, o campo `details` salvo no banco de dados especificará explicitamente a natureza do evento, evitando que a geração do link temporário seja interpretada erroneamente como a conclusão da transferência do arquivo pelo cliente.

#### Critérios de Conformidade Validada
* [x] **Geração de Registro**: Chamada integrada à função centralizada `register_audit_log` sob o status `SUCCESS` e ação `DOWNLOAD`.
* [x] **Transparência de Detalhes**: Injeção da string explicativa no parâmetro de metadados do log.
* [x] **Isolamento de Segurança**: Garantia de que logs com o status `ACCESS_DENIED` continuem disparados imediatamente caso haja quebra de isolamento de *multi-tenant* (ex: Staff do Brasil tentando ler documentos da Argentina) antes da geração do link.## 📝 Decisões de Arquitetura e Auditoria

### Rastreamento de Logs de Download (`LogAction.DOWNLOAD`)

* **Contexto**: O enum `LogAction.DOWNLOAD` foi mapeado no ecossistema da aplicação para auditar o fluxo de consumo de arquivos pelas delegações técnicas e organizadores da FIFA.
* **Decisão de Escopo**: O evento de auditoria será registrado de forma síncrona no exato momento em que a URL assinada (*Signed URL*) do Google Cloud Storage for gerada com sucesso pelo backend através do endpoint `/document/<id>/download`.
* **Justificativa Técnica**: Rastrear o download definitivo (o momento exato em que o cliente baixa os bytes do bucket do GCS) exigiria a implementação de webhooks, microsserviços de mensageria ou *callbacks* adicionais de infraestrutura em nuvem, o que foi classificado como fora de escopo para os objetivos e prazos da sprint atual.
* **Mitigação de Ambiguidades**: Para garantir total transparência e clareza para o **AUDITOR** do sistema, o campo `details` salvo no banco de dados especificará explicitamente a natureza do evento, evitando que a geração do link temporário seja interpretada erroneamente como a conclusão da transferência do arquivo pelo cliente.

#### Critérios de Conformidade Validada
* [x] **Geração de Registro**: Chamada integrada à função centralizada `register_audit_log` sob o status `SUCCESS` e ação `DOWNLOAD`.
* [x] **Transparência de Detalhes**: Injeção da string explicativa no parâmetro de metadados do log.
* [x] **Isolamento de Segurança**: Garantia de que logs com o status `ACCESS_DENIED` continuem disparados imediatamente caso haja quebra de isolamento de *multi-tenant* antes da geração do link.