<template>
  <div class="document-list">

    <!-- Estado de carregamento -->
    <p v-if="loading" class="status-msg">Carregando documentos...</p>

    <!-- Nenhum documento encontrado -->
    <p v-else-if="documents.length === 0" class="status-msg">
      Nenhum documento disponível.
    </p>

    <!-- Tabela de documentos -->
    <table v-else>
      <thead>
        <tr>
          <th>Nome</th>
          <th>Tipo</th>
          <th>Status</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="doc in documents" :key="doc.id">
          <td>{{ doc.original_name }}</td>
          <td>{{ doc.doc_type }}</td>
          <td>
            <span class="badge" :class="doc.status.toLowerCase()">
              {{ doc.status }}
            </span>
          </td>
          <td class="actions">
            <!-- Botão de Download: fica desabilitado enquanto baixa -->
            <button
              id="btn-download"
              @click="handleDownload(doc.id, doc.original_name)"
              :disabled="loadingDownload === doc.id"
              class="btn-download"
            >
              {{ loadingDownload === doc.id ? 'Baixando...' : '⬇ Baixar' }}
            </button>

            <!-- Botão de Preview (abre em nova aba) -->
            <button
              id="btn-preview"
              @click="previewDocument(doc.id)"
              class="btn-preview"
            >
              👁 Visualizar
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Mensagem de erro de download -->
    <p v-if="downloadError" class="error-msg">{{ downloadError }}</p>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDocuments } from '@/composables/useDocuments'

// Puxa os métodos e estado do composable
const { documents, loading, downloadDocument, previewDocument } = useDocuments()

// Rastreia qual documento está sendo baixado (pelo id)
const loadingDownload = ref<string | null>(null)
const downloadError = ref<string | null>(null)

async function handleDownload(docId: string, filename: string) {
  loadingDownload.value = docId
  downloadError.value = null

  try {
    await downloadDocument(docId, filename)
  } catch (error) {
    downloadError.value = error instanceof Error ? error.message : 'Falha no download. Tente novamente.'
  } finally {
    // Sempre limpa o estado de loading, mesmo se der erro
    loadingDownload.value = null
  }
}
</script>

<style scoped>
.document-list {
  padding: 1rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

th, td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

th {
  background-color: #f3f4f6;
  font-weight: 600;
  color: #374151;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn-download,
.btn-preview {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: opacity 0.2s;
}

.btn-download {
  background-color: #1d4ed8;
  color: white;
}

.btn-preview {
  background-color: #6b7280;
  color: white;
}

.btn-download:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Cores do badge de status */
.badge {
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge.pendente   { background: #fef3c7; color: #92400e; }
.badge.aprovado   { background: #d1fae5; color: #065f46; }
.badge.rejeitado  { background: #fee2e2; color: #991b1b; }

.status-msg {
  color: #6b7280;
  font-style: italic;
}

.error-msg {
  margin-top: 0.5rem;
  color: #dc2626;
  font-size: 0.9rem;
}
</style>
