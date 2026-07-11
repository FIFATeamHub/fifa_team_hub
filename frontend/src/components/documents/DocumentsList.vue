<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useDocuments, type Documento } from '@/composables/useDocuments'
import { usePermissions } from '@/composables/usePermissions';
import { useAuthStore } from '@/stores/auth.js'

const selectedType = ref('')

watch(selectedType, async () => {

    await fetchDocuments({
        doc_type: selectedType.value || undefined,
        page: 1
    })

})


const {
    documents,
    loading,
    error,
    pagination,
    fetchDocuments,
    deleteDocument,
    downloadDocument,
    previewDocument
} = useDocuments()

const { can } = usePermissions()

const authStore = useAuthStore()

// Roda fetchDocuments assim que a página/componente é carregado.
onMounted(async () => {
    await fetchDocuments()
})

function formatDate(date: string) {

    return new Date(date).toLocaleString('pt-BR')

}

async function nextPage() {
    if (pagination.value.page < pagination.value.pages) {
        await fetchDocuments({
            page: pagination.value.page + 1,
            doc_type: selectedType.value || undefined
        })
    }
}

async function previousPage() {
    if (pagination.value.page > 1) {
        await fetchDocuments({
            page: pagination.value.page - 1,
            doc_type: selectedType.value || undefined
        })
    }
}

// confirmação de delete
async function handleDelete(id: string) {

    const confirmed = confirm(
        'Tem certeza que deseja excluir este documento? Essa ação é irreversível.'
    )

    if (!confirmed) return

    await deleteDocument(id)
}

async function handleDownload(doc: Documento) {
    await downloadDocument(doc.id, doc.original_name)
}

async function handleView(doc: Documento) {
    await previewDocument(doc.id)
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

        <div v-if="!loading && !error && documents.length > 0">

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

        <table>

            <thead>

                <tr>
                    <th>Nome</th>
                    <th>Tipo</th>
                    <th>Enviado por</th>
                    <th>Data</th>
                    <th>Status</th>
                    <th>Ações</th>
                </tr>
                <th v-if="authStore.user?.role === 'ORGANIZER'">
                    Seleção
                </th>
            </thead>

            <tbody>

                <tr
                    v-for="doc in documents"
                    :key="doc.id"
                >
                <td v-if="authStore.user?.role === 'ORGANIZER'">
                    {{ doc.selection_code }}
                </td>
                
                <td>{{ doc.original_name }}</td>
                <td>{{ doc.doc_type }}</td>
                <td>{{ doc.uploaded_by_id }}</td>
                <td>{{ formatDate(doc.created_at) }}</td>
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
                        v-if="
                            can('upload:documents') &&
                            authStore.user?.id === doc.uploaded_by_id
                        "
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
        :disabled="pagination.page === 1"       
        >
        Anterior
        </button>

        <span>
            Página {{ pagination.page }} de {{ pagination.pages }}
        </span>

        <button
        @click="nextPage"
        :disabled="pagination.page >= pagination.pages || pagination.pages === 0"
        >
        Próxima
        </button>

    </div>

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