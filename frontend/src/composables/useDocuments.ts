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

export interface PendingDocument {
  doc_type: string
}

interface Pagination {
  page: number
  pages: number
  per_page: number
  total: number
}

const DEFAULT_PER_PAGE = 12

const pagination = ref<Pagination>({
  page: 1,
  pages: 0,
  per_page: DEFAULT_PER_PAGE,
  total: 0
})

export function useDocuments() {

  // Lista de documentos exibidos na tela
  const documents = ref<Documento[]>([])

  // Lista de documentos pendentes exibidos na tela
  const pendingDocuments = ref<PendingDocument[]>([])

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
              page: params?.page,
              per_page: DEFAULT_PER_PAGE
          }
      })

      documents.value = response.data.data
      pagination.value = response.data.pagination

    } catch {

      error.value = 'Erro ao carregar documentos.'

    } finally {
      loading.value = false
    }
  }

  async function fetchPendingDocuments() {

  loading.value = true
  error.value = ''

  try {

    const response = await api.get('/api/document/pending')

    pendingDocuments.value = response.data

  } catch {

    error.value = 'Erro ao carregar documentos pendentes.'

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

  
  async function resolveFileUrl(url: string): Promise<string> {
    if (/^https?:\/\//i.test(url)) {
      return url
    }

    const response = await api.get(url, { responseType: 'blob' })
    return URL.createObjectURL(response.data)
  }

  async function downloadDocument(documentId: string, filename: string) {
    try {
      const url = await getDownloadUrl(documentId)
      const resolvedUrl = await resolveFileUrl(url)

      const link = document.createElement('a')
      link.href = resolvedUrl
      link.download = filename

      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      if (resolvedUrl !== url) {
        URL.revokeObjectURL(resolvedUrl)
      }

    } catch (error) {
      const apiError = error as { response?: { status: number } }

      if (apiError.response?.status === 410) {
        throw new Error('Este documento foi removido permanentemente.')
      }

      if (apiError.response?.status === 503) {
        throw new Error('Serviço de armazenamento temporariamente indisponível. Tente novamente em instantes.')
      }

      console.error(error)
      throw error
    }
  }

  async function previewDocument(documentId: string) {
    // Abre a aba de forma síncrona, antes de qualquer await, para o navegador
    // não bloquear como pop-up (só permite window.open sem bloqueio quando
    // chamado diretamente a partir de um evento do usuário).
    const previewWindow = window.open('', '_blank')

    try {
      const url = await getDownloadUrl(documentId)
      const resolvedUrl = await resolveFileUrl(url)

      if (previewWindow) {
        previewWindow.location.href = resolvedUrl
      }
    } catch (error) {
      previewWindow?.close()
      throw error
    }
  }

  async function reviewDocument(documentId: string, status: string) {
    try {
      await api.patch(`/api/document/${documentId}/review`, { status })
      const doc = documents.value.find(d => d.id === documentId)
      if (doc) {
        doc.status = status
      }
    } catch (error) {
      const apiError = error as { response?: { status: number, data?: { error?: string } } }
      if (apiError.response?.status === 403) {
        throw new Error(apiError.response.data?.error || 'Acesso negado.')
      }
      throw new Error('Erro ao revisar documento.')
    }
  }

  return {
      documents,
      pendingDocuments,
      loading,
      error,
      pagination,
      addDocument,
      deleteDocument,
      fetchDocuments,
      fetchPendingDocuments,
      getDownloadUrl,
      downloadDocument,
      previewDocument,
      reviewDocument
  }
}