import { ref } from 'vue'
import api from '@/services/api'

// Tipo que representa um documento retornado pelo backend
export interface Documento {
  id: string
  original_name: string
  doc_type: string
  status: string
}

export function useDocuments() {
  const documents = ref<Documento[]>([])
  const loading = ref(false)

  async function getDownloadUrl(documentId: string): Promise<string> {
    const response = await api.get(`/documents/${documentId}/download`)
    return response.data.url
  }

  async function downloadDocument(documentId: string, filename: string) {
    try {
      const url = await getDownloadUrl(documentId)

      const headResponse = await api.head(url, { timeout: 5000 })
      if (headResponse.status !== 200) {
        throw new Error('URL expirada ou inválida')
      }

      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

    } catch (error) {
      const apiError = error as { response?: { status: number } }

      if (apiError.response?.status === 410) {
        console.error('Documento deletado (410 Gone)')
        throw new Error('Este documento foi removido permanentemente.')
      }
      console.error('Erro no download:', error)
      throw error
    }
  }
  async function previewDocument(documentId: string) {
    const url = await getDownloadUrl(documentId)
    window.open(url, '_blank')
  }

  return {
    documents,
    loading,
    getDownloadUrl,
    downloadDocument,
    previewDocument,
  }
}
