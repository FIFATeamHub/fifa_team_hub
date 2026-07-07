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
					href: "https://github.com/fifa_team_hub/fifa-hub",
				},
			],
			customCss: ['./src/styles/custom.css'],
			sidebar: [
				{
					label: "Início",
					items: [
						{
							label: "Sobre o Projeto",
							slug: "home/sobre",
						},
						{
							label: "Equipe",
							slug: "home/equipe",
						},
					],
				},
				{
					label: "Visão de Produto",
					items: [
						{
							label: "Contexto",
							slug: "visao/cenario",
						},
						{
							label: "Solução",
							slug: "visao/solucao",
						},
						{
							label: "Processo de Engenharia de Software",
							slug: "visao/processo-sw",
						},
						{
							label: "Cronograma",
							slug: "visao/cronograma",
						},
						{
							label: "Processo de Engenharia de Requisitos",
							slug: "visao/engenharia-requisitos",
						},
						{
							label: "Requisitos de Software",
							slug: "visao/levantamento-parcial",
						},
						{
							label: "Backlog",
							slug: "visao/backlog",
						},
					],
				},
				{
					label: "Sprints",
					items: [
						{
							label: "Semanas 7 e 8 — Planejamento",
							slug: "sprints/semanas-7-8",
						},
						{
							label: "Semanas 9 — Autenticação",
							slug: "sprints/semana-9",
						},
						{
							label: "Semanas 10 — Upload e Listagem",
							slug: "sprints/semana-10",
						},
						{
							label: "Semanas 11 — Cloud Storage",
							slug: "sprints/semana-11",
						},
					],
				},
				{
					label: "Atas de Reunião",
					items: [
						{
							label: "Reunião 01 — 28/05/2026",
							slug: "atas/reuniao-01",
						},
						{
							label: "Reunião 02 — 09/06/2026",
							slug: "atas/reuniao-02",
						},
						{
							label: "Reunião 03 — 18/06/2026",
							slug: "atas/reuniao-03",
						},
					],
				},
				{
					label: "API",
					items: [
						{
						label: "Autenticação",
						slug: "api/auth",
						},
						{
						label: "Documentos",
						slug: "api/documents",
						},
					],
				},
			],
		}),
	],
});