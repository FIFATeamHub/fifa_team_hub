async function downloadDocument(documentId: string, filename: string) {
  try {
    const url = await getDownloadUrl(documentId)
    
    // Testar se URL é válida
    const headResponse = await axios.head(url, { timeout: 5000 })
    if (headResponse.status !== 200) {
      throw new Error('URL expirada ou inválida')
    }
    
    // Prosseguir com download
    // ...
  } catch (error) {
    if (error.response?.status === 410) {
      console.error('Documento deletado (410 Gone)')
    } else {
      console.error('Erro no download:', error)
    }
  }
}