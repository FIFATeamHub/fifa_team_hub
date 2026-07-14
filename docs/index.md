# Documentação técnica — FIFA Team Hub

> **Documentação oficial publicada:** [fifateamhub.github.io/fifa_team_hub](https://fifateamhub.github.io/fifa_team_hub/) (site Astro + Starlight, publicado via GitHub Pages). Os arquivos desta pasta são a documentação técnica legada/complementar — não são publicados automaticamente, mas são mantidos em sincronia factual com o código.

## API

- [Autenticação, registro e aprovação de cadastros](api-auth.md)
- [Documentos (upload, listagem, download, revisão, exclusão)](api-documents.md)
- [Auditoria](api-audit.md)

## Arquitetura e decisões

- [Arquitetura e modelagem de dados](arquitetura.md)
- [Decisões técnicas (ADRs)](decisoes.md)
- [Diagramas UML](diagrams/uml.md)

## Deploy e infraestrutura

- [Deploy no Google Cloud Run](cloud-run-deployment.md)
- [Execução e deploy em produção (GCP)](execucao.md)
- [Setup do Google Cloud Storage](gcs-setup.md)

## Referências adicionais

- Coleções Postman: [`FIFA_Team_Hub.postman_collection.json`](FIFA_Team_Hub.postman_collection.json), [`postman/Auth Endpoints.postman_collection.json`](postman/Auth%20Endpoints.postman_collection.json)
- Requisitos e diagramas (PDF): `Requisitos FIFA hub.pdf`, `diagrama_bd_fifa.pdf`, `user_stories_fifa_team_hub-TABELA.pdf`
