import { ref } from 'vue'
import api from '@/services/api'

// Tipo que representa um documento retornado pelo backend
export interface Documento {
  id: string
  original_name: string
  doc_type: string
  file_size_kb: number
  status: string
  uploaded_by_id: string
  selection_id: string
  selection_code?: string
  created_at: string
}

interface Pagination {
  page: number
  pages: number
  per_page: number
  total: number
}

const pagination = ref<Pagination>({
  page: 1,
  pages: 0,
  per_page: 10,
  total: 0
})

export function useDocuments() {

  // Lista de documentos exibidos na tela
  const documents = ref<Documento[]>([])

  // Indica quando uma operação está em andamento (Carregando...)
  const loading = ref(false)

  // Armazena mensagens de erro para exibição na interface
  const error = ref('')

  // adiciona documento ao topo da lista (chamada após upload bem-sucedido)
  function addDocument(doc: Documento) {
    // unshift é um append no início da lista
    documents.value.unshift(doc)
  }

  async function fetchDocuments(params?: {
    doc_type?: string
    page?: number
  }) {
    loading.value = true
    error.value = ''

    try {

      const response = await api.get('/api/document/', {
          params: {
              doc_type: params?.doc_type,
              page: params?.page
          }
      })

      documents.value = response.data.data
      pagination.value = response.data.pagination

    } catch (err) {

      error.value = 'Erro ao carregar documentos.'

    } finally {
      loading.value = false
    }
  }

  async function deleteDocument(id: string) {
      try {
          await api.delete(`/api/document/${id}`)

          documents.value = documents.value.filter(
              doc => doc.id !== id
          )

      } catch {
          error.value = 'Erro ao excluir documento.'
      }
  }

  async function getDownloadUrl(documentId: string): Promise<string> {
    const response = await api.get(`/api/document/${documentId}/download`)
    return response.data.url
  }

  async function downloadDocument(documentId: string, filename: string) {
    try {
      const url = await getDownloadUrl(documentId)

      const link = document.createElement('a')
      link.href = url
      link.download = filename

      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

    } catch (error) {
      const apiError = error as { response?: { status: number } }

      if (apiError.response?.status === 410) {
        throw new Error('Este documento foi removido permanentemente.')
      }

      console.error(error)
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
    error,
    pagination,
    addDocument,
    deleteDocument,
    fetchDocuments,
    getDownloadUrl,
    downloadDocument,
    previewDocument,
  }
}