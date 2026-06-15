import { computed, ref } from 'vue'

//define como um documento deve ser
export interface Documento {
  id: string
  original_name: string
  doc_type: string
  file_size_kb: number
  status: string
  uploaded_by_name: string
  selection_code: string
  created_at: string
}

export function useDocuments() {

    // Lista de documentos exibidos na tela
    const documents = ref<Documento[]>([])

    // Indica quando uma operação está em andamento (Carregando...)
    const loading = ref(false)

    // Armazena mensagens de erro para exibição na interface
    const error = ref('')

    // adiciona documento ao topo da lista (chamada após upload bem-sucedido)
    function addDocument(doc: Documento) {

        // unshift é um append no inicio da lista
        documents.value.unshift(doc)

    }

    async function fetchDocuments() {
        
        

        loading.value = true
        error.value = ''

        // chamada da api
        try {

            //futuramente:
            //const response = await api.get(...)

            documents.value = []
        } 
        // se der errado
        catch (err){

            error.value = 'Erro ao carregar documentos.'

        } 
        // executa sempre após
        finally {

            loading.value = false

        }
    }
        
    
    function deleteDocument(id: string) {

        documents.value = documents.value.filter(
            doc => doc.id !== id
        )
    }


    return {
        documents,
        loading,
        error,
        addDocument,
        deleteDocument,
        fetchDocuments
    }

}