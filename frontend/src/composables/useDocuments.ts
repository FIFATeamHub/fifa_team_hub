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

  // Busca a URL assinada do GCS para um documento específico.
  // O backend é quem gera a URL — o frontend só a recebe e usa.
  async function getDownloadUrl(documentId: string): Promise<string> {
    const response = await api.get(`/documents/${documentId}/download`)
    return response.data.url
  }

  // Faz o download do arquivo criando um <a> invisível e simulando o clique.
  // Isso evita abrir uma nova aba e força o navegador a baixar o arquivo.
  async function downloadDocument(documentId: string, filename: string) {
    try {
      const url = await getDownloadUrl(documentId)

      // Testa se a URL ainda é válida antes de baixar
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

    } catch (error: any) {
      // 410 = documento foi deletado do GCS
      if (error.response?.status === 410) {
        console.error('Documento deletado (410 Gone)')
        throw new Error('Este documento foi removido permanentemente.')
      }
      console.error('Erro no download:', error)
      throw error
    }
  }

  // Abre o documento em uma nova aba para preview (PDF e imagens)
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
