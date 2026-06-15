<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useDocuments, type Documento } from '@/composables/useDocuments'
declare module '@/composables/usePermissions'
import { usePermissions } from '@/composables/usePermissions';
import { useAuthStore } from '@/stores/auth.js'

const selectedType = ref('')

const currentPage = ref(1)

const totalPages = computed(() => {

    return Math.ceil(
        filteredDocuments.value.length / itemsPerPage
    )
    
})

const itemsPerPage = 10

const filteredDocuments = computed(() => {

    let docs = documents.value

    // Restrição do ORGANIZER
    if (authStore.user?.role === 'ORGANIZER') {

        docs = docs.filter(doc =>
            doc.doc_type === 'PASSAPORTE' ||
            doc.doc_type === 'CONVOCACAO'
        )

    }

    // Filtro selecionado pelo usuário
    if (!selectedType.value) {
        return docs
    }

    return docs.filter(doc =>
        doc.doc_type === selectedType.value
    )

})


const paginatedDocuments = computed(() => {

    const start = (currentPage.value - 1) * itemsPerPage

    const end = start + itemsPerPage

    return filteredDocuments.value.slice(start, end)

})



const {
    documents,
    loading,
    error,
    fetchDocuments,
    deleteDocument
} = useDocuments()

const { can } = usePermissions()

const authStore = useAuthStore()

// Roda fetchDocuments assim que a página/componente é carregado.
onMounted(() => {
    fetchDocuments()
})

function nextPage() {

    if (currentPage.value < totalPages.value) {
        currentPage.value++
    }

}

function previousPage() {

    if (currentPage.value > 1) {
        currentPage.value--
    }

}

// confirmação de delete
function handleDelete(id: string) {

    const confirmed = confirm(
        'Tem certeza que deseja excluir este documento? Essa ação é irreversível.'
    )

    if (!confirmed) {
        return
    }

    deleteDocument(id)
}

function handleDownload(doc: Documento) {

    alert(`Baixando ${doc.original_name}`)

}

function handleView(doc: Documento) {

    alert(`Visualizar ${doc.original_name}`)

}

</script>

<template>

    <div>

        <h2>Documentos</h2>

        <div v-if="loading" class="spinner-container">
            <div class="spinner"></div>
                <p>Carregando documentos...</p>
        </div>

        <p v-else-if="error">{{ error }}</p>

        <p v-else-if="documents.length === 0">Nenhum documento foi encontrado.</p>

        <table v-else>

            <thead>

                <div class="filtros">
    
                    <select v-model="selectedType">
    
                        <option value="">
                            Todos os tipos
                        </option>
    
                        <option value="PASSAPORTE">
                            Passaporte
                        </option>
    
                        <option value="CONVOCADO">
                            Convocação
                        </option>
    
                        <option value="LAUDO_MEDICO">
                            Laudo Médico
                        </option>
    
                        <option value="RELATORIO_TATICO">
                            Relatório Tático
                        </option>
    
                    </select>
    
                    <p>Filtro selecionado: {{ selectedType }}</p>
    
                    <button @click="selectedType = ''">Limpar filtros</button>
    
                </div>

                <tr>
                    <th>Nome</th>
                    <th>Tipo</th>
                    <th>Enviado por</th>
                    <th>Data</th>
                    <th>Status</th>
                    <th>Ações</th>
                </tr>
            </thead>

            <tbody>


                <tr
                    v-for="doc in paginatedDocuments"
                    :key="doc.id"
                >
            
                <td>{{ doc.original_name }}</td>
                <td>{{ doc.doc_type }}</td>
                <td>{{ doc.uploaded_by_name }}</td>
                <td>{{ doc.created_at }}</td>
                <!--status-->
                <td>

                    <span
                        v-if="doc.status === 'APPROVED'"
                        class="badge aprovado"
                    >
                        Aprovado
                    </span>

                    <span
                        v-else-if="doc.status === 'PENDING'"
                        class="badge pendente"
                    >
                        Pendente
                    </span>

                    <span
                        v-else-if="doc.status === 'REJECTED'"
                        class="badge rejeitado"
                    >
                        Rejeitado
                    </span>


                </td>

                <td>

                    <button 
                        @click="handleView(doc)">
                            Visualizar
                    </button>

                </td>

                <td>

                    <button
                        @click="handleDownload(doc)">
                            Baixar
                    </button>

                </td>

                <td>

                    <button
                        v-if="can('upload:documents')"
                        @click="handleDelete(doc.id)">
                            Deletar
                    </button>

                </td>

            </tr>

            </tbody>

        </table>

    </div>

    <div class="pagination">

        <button
        @click="previousPage"
        :disabled="currentPage === 1"        
        >
        Anterior
        </button>

        <span>
            Página {{ currentPage }} de {{ totalPages }}
        </span>

        <button
        @click="nextPage"
        :disabled="currentPage === totalPages"
        >
        Próxima
        </button>

    </div>

</template>


<style scoped>

.badge {
    padding: 0.4rem 0.8rem;
    border-radius: 0.5rem;
    font-size: 0.85rem;
    font-weight: bold;
}

.aprovado {
    background: #d4edda;
}

.pendente {
    background: #fff3cd;
}

.rejeitado {
    background: #f8d7da;
}

.spinner {
    width: 40px;
    height: 40px;

    border: 4px solid #ddd;
    border-top: 4px solid #3498db;

    border-radius: 50%;

    animation: spin 1s linear infinite;
}

.spinner-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    padding: 2rem;
}

@keyframes spin {

    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }

}

</style>