// @ts-check

import starlight from "@astrojs/starlight";
import { defineConfig } from "astro/config";
import starlightThemeRapidePlugin from "starlight-theme-rapide";

export default defineConfig({
	site: "https://fifateamhub.github.io",
	base: "/fifa_team_hub/",
	markdown:{
		gfm:true,
	},
	integrations: [
		starlight({
			plugins: [starlightThemeRapidePlugin()],
			title: "FIFA Team Hub",
			social: [
				{
					icon: "github",
					label: "GitHub",
					href: "https://github.com/FIFATeamHub/fifa_team_hub",
				},
			],
			customCss: ['./src/styles/custom.css'],
			sidebar: [
				{
					label: "Início",
					items: [
						{
							label: "Visão Geral do Projeto",
							slug: "home/sobre",
						},
						{
							label: "Equipe",
							slug: "home/equipe",
						},
					],
				},
				{
					label: "Features Principais",
					items: [
						{
							label: "Isolamento de Seleções",
							slug: "features/isolamento-selecoes",
						},
						{
							label: "Auditoria de Segurança",
							slug: "features/auditoria-seguranca",
						},
						{
							label: "Upload de Documentos Sensíveis",
							slug: "features/upload-documentos",
						},
						{
							label: "Controle de Acesso (RBAC)",
							slug: "features/controle-acesso",
						},
					],
				},
				{
					label: "Arquitetura & Cloud",
					items: [
						{
							label: "Visão Geral da Arquitetura",
							slug: "architecture/visao-geral",
						},
						{
							label: "Stack Tecnológico",
							slug: "architecture/stack-tecnologico",
						},
						{
							label: "Armazenamento & Google Cloud Storage",
							slug: "architecture/armazenamento-gcs",
						},
						{
							label: "Segurança e Isolamento de Dados",
							slug: "architecture/seguranca-dados",
						},
					],
				},
				{
					label: "Deploy & CI/CD",
					items: [
						{
							label: "Pipeline de CI (GitHub Actions)",
							slug: "deploy/ci-pipeline",
						},
						{
							label: "Deploy em Cloud Run (Cloud Build + GCR)",
							slug: "deploy/deploy-cloud-run",
						},
						{
							label: "Ambiente Local (Docker Compose)",
							slug: "deploy/ambiente-local",
						},
					],
				},
				{
					label: "Referência de API",
					items: [
						{
							label: "Autenticação",
							slug: "api/auth",
						},
						{
							label: "Documentos",
							slug: "api/documents",
						},
						{
							label: "Auditoria",
							slug: "api/auditoria",
						},
					],
				},
				{
					label: "Processo & Entregas",
					items: [
						{
							label: "Processo de Desenvolvimento",
							slug: "home/processo",
						},
						{
							label: "Visão de Produto",
							items: [
								{ label: "Contexto", slug: "visao/cenario" },
								{ label: "Solução", slug: "visao/solucao" },
								{ label: "Processo de Engenharia de Software", slug: "visao/processo-sw" },
								{ label: "Cronograma", slug: "visao/cronograma" },
								{ label: "Processo de Engenharia de Requisitos", slug: "visao/engenharia-requisitos" },
								{ label: "Requisitos de Software", slug: "visao/levantamento-parcial" },
								{ label: "Backlog", slug: "visao/backlog" },
							],
						},
						{
							label: "Sprints",
							items: [
								{ label: "Semanas 7 e 8 — Planejamento", slug: "sprints/semanas-7-8" },
								{ label: "Semana 9 — Autenticação", slug: "sprints/semana-9" },
								{ label: "Semana 10 — Upload e Listagem", slug: "sprints/semana-10" },
								{ label: "Semana 11 — Cloud Storage", slug: "sprints/semana-11" },
							],
						},
						{
							label: "Atas de Reunião",
							items: [
								{ label: "Reunião 01 — 28/05/2026", slug: "atas/reuniao-01" },
								{ label: "Reunião 02 — 09/06/2026", slug: "atas/reuniao-02" },
								{ label: "Reunião 03 — 18/06/2026", slug: "atas/reuniao-03" },
							],
						},
					],
				},
			],
		}),
	],
});
