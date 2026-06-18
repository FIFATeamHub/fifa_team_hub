<template>
  <div class="document-list">
    <table>
      <tbody>
        <tr v-for="doc in documents" :key="doc.id">
          <td>{{ doc.original_name }}</td>
          <td>{{ doc.doc_type }}</td>
          <td>
            <span class="badge" :class="doc.status">
              {{ doc.status }}
            </span>
          </td>
          <td>
            <!-- Botão Download -->
            <button 
              @click="handleDownload(doc.id, doc.original_name)"
              :disabled="loadingDownload === doc.id"
            >
              {{ loadingDownload === doc.id ? 'Baixando...' : 'Baixar' }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
 
<script setup lang="ts">
import { ref } from 'vue'
import { useDocuments } from '@/composables/useComponents'
 
const { downloadDocument } = useDocuments()
const loadingDownload = ref<string | null>(null)
 
const handleDownload = async (docId: string, filename: string) => {
  loadingDownload.value = docId
  try {
    await downloadDocument(docId, filename)
  } finally {
    loadingDownload.value = null
  }
}
</script>