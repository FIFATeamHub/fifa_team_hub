// @ts-check

import starlight from "@astrojs/starlight";
import { defineConfig } from "astro/config";
import starlightThemeRapidePlugin from "starlight-theme-rapide";

export default defineConfig({
	site: "https://fifa_team_hub.github.io",
	base: "/fifa_team_hub/",
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
					label: "Visões de Produto e de Projeto",
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
							label: "Comunicação e Colaboração",
							slug: "visao/interacao",
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
					label: "Lições Aprendidas",
					items: [
						{
							label: "Unidade 1",
							slug: "licoes/unidade-1",
						},
					],
				},
			],
		}),
	],
});