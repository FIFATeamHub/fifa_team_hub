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

onMounted(async () => {
    await fetchDocuments()
})

function formatDate(date: string) {

    return new Date(date).toLocaleString('pt-BR')

}

const docTypeLabels: Record<string, string> = {
    PASSPORT: 'Passaporte',
    CONVOCADO: 'Convocação',
    LAUDO_MEDICO: 'Laudo Médico',
    RELATORIO_TATICO: 'Relatório Tático',
    ESQUEMA_JOGADAS: 'Esquema de Jogadas'
}

function formatDocType(type: string) {
    return docTypeLabels[type] ?? type
}

const statusLabels: Record<string, string> = {
    APPROVED: 'Aprovado',
    PENDING: 'Em revisão',
    REJECTED: 'Restrito'
}

function statusLabel(status: string) {
    return statusLabels[status] ?? status
}

function statusBadgeClass(status: string) {
    if (status === 'APPROVED') return 'doc-card__badge--success'
    if (status === 'PENDING') return 'doc-card__badge--warning'
    if (status === 'REJECTED') return 'doc-card__badge--danger'
    return ''
}

function statusAccentClass(status: string) {
    if (status === 'APPROVED') return 'doc-card--success'
    if (status === 'PENDING') return 'doc-card--warning'
    if (status === 'REJECTED') return 'doc-card--danger'
    return ''
}

const docTypeIcons: Record<string, string> = {
    PASSPORT: 'id',
    CONVOCADO: 'clipboard',
    LAUDO_MEDICO: 'pulse',
    RELATORIO_TATICO: 'chart',
    ESQUEMA_JOGADAS: 'flag'
}

function docTypeIcon(type: string) {
    return docTypeIcons[type] ?? 'file'
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

async function handleDelete(id: string) {

    const confirmed = confirm(
        'Tem certeza que deseja excluir este documento? Essa ação é irreversível.'
    )

    if (!confirmed) return

    await deleteDocument(id)
}

async function handleDownload(doc: Documento) {
    try {
        await downloadDocument(doc.id, doc.original_name)
    } catch (err) {
        alert(err instanceof Error ? err.message : 'Falha ao baixar o documento.')
    }
}

async function handleView(doc: Documento) {
    try {
        await previewDocument(doc.id)
    } catch (err) {
        alert(err instanceof Error ? err.message : 'Falha ao visualizar o documento.')
    }
}

</script>

<template>

    <div class="documents">

        <div class="documents__toolbar">

            <div class="documents__filter">
                <label for="doc-type-filter" class="documents__filter-label">Filtro</label>
                <div class="documents__select-wrap">
                    <svg class="documents__select-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M4 5h16l-6 8v6l-4-2v-4Z" />
                    </svg>
                    <select id="doc-type-filter" v-model="selectedType" class="documents__select">
                        <option value="">Todos</option>
                        <option value="PASSPORT">Passaporte</option>
                        <option value="CONVOCADO">Convocação</option>
                        <option value="LAUDO_MEDICO">Laudo Médico</option>
                        <option value="RELATORIO_TATICO">Relatório Tático</option>
                    </select>
                    <svg class="documents__select-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M6 9l6 6 6-6" />
                    </svg>
                </div>
            </div>

        </div>

        <div v-if="!loading && !error" class="documents__stats">
            <span>{{ pagination.total }} documento{{ pagination.total === 1 ? '' : 's' }}</span>
            <span v-if="pagination.pages > 0">Página {{ pagination.page }} de {{ pagination.pages }}</span>
        </div>

        <div v-if="loading" class="documents__state">
            <div class="documents__spinner"></div>
            <p>Carregando documentos...</p>
        </div>

        <p v-else-if="error" class="documents__error">{{ error }}</p>

        <p v-else-if="documents.length === 0" class="documents__empty">Nenhum documento foi encontrado.</p>

        <div v-else class="documents__grid">

            <article
                v-for="doc in documents"
                :key="doc.id"
                class="doc-card"
                :class="statusAccentClass(doc.status)"
            >

                <header class="doc-card__header">

                    <span class="doc-card__icon">
                        <svg v-if="docTypeIcon(doc.doc_type) === 'id'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="5" width="18" height="14" rx="2" />
                            <circle cx="9" cy="11" r="2" />
                            <path d="M15 10h3M15 14h3M6 16c.5-1.8 2-2.5 3-2.5s2.5.7 3 2.5" />
                        </svg>
                        <svg v-else-if="docTypeIcon(doc.doc_type) === 'clipboard'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M9 4h6a1 1 0 0 1 1 1v1H8V5a1 1 0 0 1 1-1Z" />
                            <path d="M6 6h12v14H6z" />
                            <path d="M9 12l2 2 4-4" />
                        </svg>
                        <svg v-else-if="docTypeIcon(doc.doc_type) === 'pulse'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M3 12h4l2-7 4 14 2-7h6" />
                        </svg>
                        <svg v-else-if="docTypeIcon(doc.doc_type) === 'chart'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M4 20V10M12 20V4M20 20v-7" />
                        </svg>
                        <svg v-else-if="docTypeIcon(doc.doc_type) === 'flag'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M5 3v18" />
                            <path d="M5 4h13l-3 4 3 4H5" />
                        </svg>
                        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M7 3h7l5 5v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z" />
                            <path d="M14 3v5h5" />
                        </svg>
                    </span>

                    <span class="doc-card__badge" :class="statusBadgeClass(doc.status)">
                        {{ statusLabel(doc.status) }}
                    </span>

                </header>

                <h3 class="doc-card__title">{{ doc.original_name }}</h3>

                <dl class="doc-card__meta">

                    <div class="doc-card__meta-row">
                        <dt>Categoria</dt>
                        <dd>{{ formatDocType(doc.doc_type) }}</dd>
                    </div>

                    <div
                        v-if="authStore.user?.role === 'ORGANIZER' && doc.selection_code"
                        class="doc-card__meta-row"
                    >
                        <dt>Seleção</dt>
                        <dd>{{ doc.selection_code }}</dd>
                    </div>

                    <div class="doc-card__meta-row">
                        <dt>Atualizado</dt>
                        <dd>{{ formatDate(doc.created_at) }}</dd>
                    </div>

                </dl>

                <div class="doc-card__divider"></div>

                <div class="doc-card__actions">

                    <button class="doc-card__action" @click="handleView(doc)">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M1.5 12S5 5 12 5s10.5 7 10.5 7-3.5 7-10.5 7-10.5-7-10.5-7Z" />
                            <circle cx="12" cy="12" r="3" />
                        </svg>
                        Visualizar
                    </button>

                    <button class="doc-card__action" @click="handleDownload(doc)">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 3v12m0 0 4-4m-4 4-4-4" />
                            <path d="M4 19h16" />
                        </svg>
                        Baixar
                    </button>

                    <button
                        v-if="
                            can('upload:documents') &&
                            authStore.user?.id === doc.uploaded_by_id
                        "
                        class="doc-card__action doc-card__action--danger"
                        @click="handleDelete(doc.id)"
                    >
                        Excluir
                    </button>

                </div>

            </article>

        </div>

        <div v-if="!loading && !error && documents.length > 0" class="documents__pagination">

            <button
                class="documents__page-btn documents__page-btn--secondary"
                @click="previousPage"
                :disabled="pagination.page === 1"
            >
                Página anterior
            </button>

            <button
                class="documents__page-btn documents__page-btn--primary"
                @click="nextPage"
                :disabled="pagination.page >= pagination.pages || pagination.pages === 0"
            >
                Próxima página
            </button>

        </div>

    </div>

</template>


<style scoped>

.documents {
    display: flex;
    flex-direction: column;
    gap: var(--space-8);
}

.documents__toolbar {
    display: flex;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: var(--space-6);
}

.documents__filter {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
}

.documents__filter-label {
    font-family: var(--font-mono);
    font-size: var(--font-size-label);
    letter-spacing: var(--letter-spacing-label);
    text-transform: uppercase;
    color: var(--color-gold);
}

.documents__select-wrap {
    position: relative;
    display: inline-flex;
    align-items: center;
}

.documents__select {
    appearance: none;
    -webkit-appearance: none;
    padding: var(--space-3) var(--space-8) var(--space-3) var(--space-10);
    background-color: var(--color-surface-elevated);
    border: 1px solid var(--color-border-gold);
    border-radius: var(--radius-full);
    color: var(--color-text-primary);
    font-family: var(--font-body);
    font-weight: var(--font-weight-semibold);
    font-size: var(--font-size-body);
    cursor: pointer;
    transition: border-color var(--transition-default);
}

.documents__select:focus {
    outline: none;
    border-color: var(--color-border-gold-full);
}

.documents__select-icon {
    position: absolute;
    left: var(--space-4);
    width: 14px;
    height: 14px;
    color: var(--color-gold);
    pointer-events: none;
}

.documents__select-chevron {
    position: absolute;
    right: var(--space-4);
    width: 14px;
    height: 14px;
    color: var(--color-text-tertiary);
    pointer-events: none;
}

.documents__stats {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-family: var(--font-mono);
    font-size: var(--font-size-label);
    letter-spacing: var(--letter-spacing-mono);
    text-transform: uppercase;
    color: var(--color-text-tertiary);
}

.documents__state {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-12);
    color: var(--color-text-secondary);
    font-family: var(--font-body);
    font-size: var(--font-size-body);
}

.documents__spinner {
    width: 32px;
    height: 32px;
    border: 3px solid var(--color-border-default);
    border-top-color: var(--color-gold);
    border-radius: var(--radius-full);
    animation: documents-spin 1s linear infinite;
}

@keyframes documents-spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.documents__error {
    padding: var(--space-4);
    background-color: var(--color-danger-bg);
    border: 1px solid var(--color-danger-border);
    border-radius: var(--radius-sm);
    color: var(--color-danger);
    font-family: var(--font-body);
    font-size: var(--font-size-body);
}

.documents__empty {
    padding: var(--space-8);
    text-align: center;
    color: var(--color-text-tertiary);
    font-family: var(--font-mono);
    font-size: var(--font-size-label);
    letter-spacing: var(--letter-spacing-mono);
    text-transform: uppercase;
}

.documents__grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(20rem, 1fr));
    gap: var(--space-6);
}

.doc-card {
    position: relative;
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    padding: var(--padding-card);
    background-color: var(--color-surface-elevated);
    border: 1px solid var(--color-border-default);
    border-left: 3px solid var(--color-border-default);
    border-radius: var(--radius-xl);
    overflow: hidden;
    transition: transform var(--transition-default), border-color var(--transition-default);
}

.doc-card:hover {
    transform: translateY(-4px);
    border-color: var(--color-border-gold);
}

.doc-card--success {
    border-left-color: var(--color-teal);
}

.doc-card--warning {
    border-left-color: var(--color-gold);
}

.doc-card--danger {
    border-left-color: var(--color-danger);
}

.doc-card__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.doc-card__icon {
    position: relative;
    z-index: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    background-color: var(--color-warning-bg);
    border: 1px solid var(--color-border-gold);
    border-radius: var(--radius-md);
    color: var(--color-gold);
}

.doc-card__icon svg {
    width: 22px;
    height: 22px;
}

.doc-card__badge {
    padding: var(--space-1) var(--space-3);
    border-radius: var(--radius-full);
    font-family: var(--font-mono);
    font-size: var(--font-size-label);
    font-weight: var(--font-weight-bold);
    letter-spacing: var(--letter-spacing-label);
    text-transform: uppercase;
}

.doc-card__badge--success {
    background-color: var(--color-success-bg);
    color: var(--color-teal-light);
}

.doc-card__badge--warning {
    background-color: var(--color-warning-bg);
    color: var(--color-gold);
}

.doc-card__badge--danger {
    background-color: var(--color-danger-bg);
    color: var(--color-danger);
}

.doc-card__title {
    font-family: var(--font-heading);
    font-weight: var(--font-weight-bold);
    font-size: var(--font-size-h3);
    letter-spacing: var(--letter-spacing-heading);
    color: var(--color-text-primary);
}

.doc-card__meta {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
}

.doc-card__meta-row {
    display: flex;
    justify-content: space-between;
    gap: var(--space-3);
    font-family: var(--font-body);
    font-size: var(--font-size-small);
}

.doc-card__meta-row dt {
    color: var(--color-text-tertiary);
}

.doc-card__meta-row dd {
    color: var(--color-text-secondary);
    font-weight: var(--font-weight-semibold);
    text-align: right;
}

.doc-card__divider {
    height: 1px;
    background-color: var(--color-border-default);
}

.doc-card__actions {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-3);
}

.doc-card__action {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
    flex: 1;
    padding: var(--space-2) var(--space-4);
    background: none;
    border: 1px solid var(--color-border-default);
    border-radius: var(--radius-sm);
    color: var(--color-text-secondary);
    font-family: var(--font-body);
    font-weight: var(--font-weight-semibold);
    font-size: var(--font-size-small);
    cursor: pointer;
    transition: border-color var(--transition-default), color var(--transition-default);
}

.doc-card__action svg {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
}

.doc-card__action:hover {
    border-color: var(--color-border-teal);
    color: var(--color-teal-light);
}

.doc-card__action--danger {
    color: var(--color-danger);
    border-color: var(--color-danger-border);
}

.doc-card__action--danger:hover {
    border-color: var(--color-danger);
    color: var(--color-danger);
}

.documents__pagination {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-4);
}

.documents__page-btn {
    padding: var(--space-3) var(--space-6);
    border-radius: var(--radius-full);
    font-family: var(--font-body);
    font-weight: var(--font-weight-semibold);
    font-size: var(--font-size-small);
    cursor: pointer;
    transition: border-color var(--transition-default), color var(--transition-default), background-color var(--transition-default);
}

.documents__page-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

.documents__page-btn--secondary {
    background: none;
    border: 1px solid var(--color-border-default);
    color: var(--color-text-secondary);
}

.documents__page-btn--secondary:hover:not(:disabled) {
    border-color: var(--color-border-teal);
    color: var(--color-teal-light);
}

.documents__page-btn--primary {
    border: 1px solid var(--color-gold);
    background-color: var(--color-gold);
    color: var(--color-bg-deep);
    font-weight: var(--font-weight-black);
}

.documents__page-btn--primary:hover:not(:disabled) {
    background-color: var(--color-gold-hover);
    border-color: var(--color-gold-hover);
}

.documents__page-btn--primary:disabled {
    background-color: var(--color-surface-elevated);
    border-color: var(--color-border-default);
    color: var(--color-text-tertiary);
}

@media (max-width: 480px) {
    .documents__grid {
        grid-template-columns: 1fr;
    }
}

</style>
