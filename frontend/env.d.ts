/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// Ignora erros ao importar arquivos JS não tipados
declare module '@/services/api';
declare module './router/index.js';
