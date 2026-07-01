import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node', // ou 'jsdom' se for testar componentes web
  },
});