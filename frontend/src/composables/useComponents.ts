import axios from 'axios'
 
export function useDocuments() {
  const documents = ref([])
  const loading = ref(false)
 
  // Novo: método para gerar URL de download assinada
  async function getDownloadUrl(documentId: string): Promise<string> {
    try {
      const response = await axios.get(`/documents/${documentId}/download`)
      return response.data.url // URL assinada do GCS ou local
    } catch (error) {
      throw new Error(`Erro ao gerar URL: ${error}`)
    }
  }
 
  // Download via link assinado
  async function downloadDocument(documentId: string, filename: string) {
    try {
      const url = await getDownloadUrl(documentId)
      
      // Criar elemento temporário e simular click
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (error) {
      console.error('Download falhou:', error)
    }
  }
 
  return {
    documents,
    loading,
    getDownloadUrl,
    downloadDocument
  }
}