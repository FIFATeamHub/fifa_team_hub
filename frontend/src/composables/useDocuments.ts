import { ref } from 'vue'
import axios from 'axios'

export function useDocuments() {
  const documents = ref([])
  const loading = ref(false)

  async function getDownloadUrl(documentId: string): Promise<string> {
    try {
      const response = await axios.get(`/documents/${documentId}/download`)
      return response.data.url
    } catch (error) {
      throw new Error(`Erro ao gerar URL: ${error}`)
    }
  }

  async function downloadDocument(documentId: string, filename: string) {
    try {
      const url = await getDownloadUrl(documentId)
      
      const headResponse = await axios.head(url, { timeout: 5000 })
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
      if (error.response?.status === 410) {
        console.error('Documento deletado (410 Gone)')
      } else {
        console.error('Erro no download:', error)
      }
    }
  }

  return {
    documents,
    loading,
    getDownloadUrl,
    downloadDocument
  }
}