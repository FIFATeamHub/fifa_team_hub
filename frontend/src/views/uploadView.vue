<template>
    <div class="upload-view">

        <section class="upload-view__hero">
            <div class="upload-view__hero-bg"></div>
            <div class="upload-view__hero-overlay"></div>
            <div class="upload-view__hero-edge"></div>

            <div class="upload-view__hero-content">
                <h1 class="upload-view__hero-title">
                    Upload
                    <span class="upload-view__hero-title--muted">de arquivos</span>
                </h1>
            </div>
        </section>

        <div class="upload-view__content">

            <div v-if="can('upload:documents')" class="upload-view__layout">

            <div class="upload-view__panel">

                <div
                    class="upload-view__dropzone"
                    :class="{
                        'upload-view__dropzone--active': isDragging,
                        'upload-view__dropzone--filled': !!selectedFile
                    }"
                    @dragover.prevent="isDragging = true"
                    @dragleave.prevent="isDragging = false"
                    @drop.prevent="handleDrop"
                >
                    <span class="upload-view__dropzone-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 15V4m0 0-4 4m4-4 4 4" stroke-linecap="round" stroke-linejoin="round" />
                            <path d="M4 15v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3" stroke-linecap="round" stroke-linejoin="round" />
                        </svg>
                    </span>

                    <p class="upload-view__dropzone-title">
                        {{ selectedFile ? selectedFile.name : 'Arraste arquivos aqui' }}
                    </p>

                    <p v-if="!selectedFile" class="upload-view__dropzone-hint">
                        ou <span class="upload-view__dropzone-link">clique para selecionar</span> do dispositivo
                    </p>
                    <p v-else class="upload-view__dropzone-hint">
                        Clique para selecionar outro arquivo
                    </p>

                    <div class="upload-view__tags">
                        <span class="upload-view__tag">PDF</span>
                        <span class="upload-view__tag">DOCX</span>
                        <span class="upload-view__tag">JPG</span>
                        <span class="upload-view__tag">PNG</span>
                        <span class="upload-view__tag">máx. 10MB</span>
                    </div>

                    <input
                        type="file"
                        class="upload-view__file-input"
                        accept=".pdf,.jpg,.jpeg,.png,.docx"
                        :disabled="isLoading"
                        @change="handleFileChange"
                    />
                </div>

                <div class="upload-view__classification">

                    <p class="upload-view__section-label">
                        <span class="upload-view__section-label-line"></span>
                        Classificação do arquivo
                    </p>

                    <div class="upload-view__field">
                        <label class="upload-view__label" for="upload-category">Categoria</label>
                        <div class="upload-view__select-wrap">
                            <select
                                id="upload-category"
                                v-model="selectedType"
                                class="upload-view__select"
                                :disabled="isLoading"
                            >
                                <option value="" disabled>Selecione uma categoria</option>
                                <option value="CONVOCADO">Convocação</option>
                                <option value="PASSPORT">Passaporte</option>
                                <option value="LAUDO_MEDICO">Laudo Médico</option>
                                <option value="RELATORIO_TATICO">Relatório Tático</option>
                                <option value="ESQUEMA_JOGADAS">Esquema de Jogadas</option>
                            </select>
                            <svg class="upload-view__select-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M6 9l6 6 6-6" stroke-linecap="round" stroke-linejoin="round" />
                            </svg>
                        </div>
                    </div>

                </div>

                <div v-if="isLoading" class="upload-view__progress">
                    <div class="upload-view__progress-bar" :style="{ width: uploadProgress + '%' }"></div>
                    <span class="upload-view__progress-label">{{ uploadProgress }}%</span>
                </div>

                <p v-if="errorMessage" class="upload-view__error">{{ errorMessage }}</p>

                <button
                    class="upload-view__submit-btn"
                    :disabled="!isFormValid || isLoading"
                    @click="handleSubmit"
                >
                    {{ isLoading ? 'Enviando...' : 'Enviar arquivo' }}
                </button>

            </div>

            <aside class="upload-view__aside">

                <div class="upload-view__info-card">
                    <p class="upload-view__section-label">
                        <span class="upload-view__section-label-line"></span>
                        Como funciona
                    </p>

                    <ol class="upload-view__steps">
                        <li class="upload-view__step">
                            <span class="upload-view__step-index">01</span>
                            <div>
                                <p class="upload-view__step-title">Selecione o arquivo</p>
                                <p class="upload-view__step-text">PDF, DOCX, JPG ou PNG, até 10MB.</p>
                            </div>
                        </li>
                        <li class="upload-view__step">
                            <span class="upload-view__step-index">02</span>
                            <div>
                                <p class="upload-view__step-title">Classifique por categoria</p>
                                <p class="upload-view__step-text">Convocação, passaporte, laudo médico, relatório tático ou esquema de jogadas.</p>
                            </div>
                        </li>
                        <li class="upload-view__step">
                            <span class="upload-view__step-index">03</span>
                            <div>
                                <p class="upload-view__step-title">Envio registrado</p>
                                <p class="upload-view__step-text">O documento segue para revisão, com status aprovado, pendente ou recusado.</p>
                            </div>
                        </li>
                    </ol>
                </div>

                <div class="upload-view__info-card">
                    <p class="upload-view__section-label">
                        <span class="upload-view__section-label-line"></span>
                        Rastreabilidade
                    </p>

                    <p class="upload-view__info-text">
                        Todo envio, aprovado ou recusado, fica registrado na trilha de auditoria do sistema, com usuário, data e status.
                    </p>
                </div>

            </aside>

            </div>

            <p v-else class="upload-view__empty">
                Seu perfil não possui permissão para enviar documentos.
            </p>

        </div>

    </div>
</template>

<script setup lang="ts">

import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { usePermissions } from '@/composables/usePermissions'
import { uploadDocument } from '@/services/documentService.js'

const { can } = usePermissions()
const router = useRouter()

const selectedFile   = ref<File | null>(null)
const selectedType   = ref('')
const isDragging     = ref(false)
const uploadProgress = ref(0)
const isLoading      = ref(false)
const errorMessage   = ref('')

const isFormValid = computed(() =>
    selectedFile.value !== null && selectedType.value !== ''
)

function applyFile(arquivo: File | null | undefined) {
    errorMessage.value = ''

    if (arquivo && arquivo.size > 10 * 1024 * 1024) {
        errorMessage.value = 'O ficheiro excede o limite de 10 MB.'
        selectedFile.value = null
        return
    }

    selectedFile.value = arquivo ?? null
}

function handleFileChange(event: Event) {
    const input = event.target as HTMLInputElement
    applyFile(input.files?.[0])
}

function handleDrop(event: DragEvent) {
    isDragging.value = false
    applyFile(event.dataTransfer?.files?.[0])
}

async function handleSubmit() {
    if (!isFormValid.value || !selectedFile.value) return

    isLoading.value      = true
    errorMessage.value   = ''
    uploadProgress.value = 0

    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('doc_type', selectedType.value)

    try {
        await uploadDocument(formData, (progressEvent: { loaded: number; total: number }) => {
            uploadProgress.value = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
            )
        })

        router.push('/documentos')

    } catch (erro) {
        const err = erro as { response?: { status?: number } }
        const status = err.response?.status

        const mensagens: Record<number, string> = {
            403: 'Não tem permissão para enviar documentos.',
            413: 'O ficheiro excede o limite permitido pelo servidor.',
            415: 'Formato de ficheiro não suportado pelo servidor.',
        }

        errorMessage.value = (status !== undefined ? mensagens[status] : undefined) ?? 'Erro ao enviar documento. Tente novamente.'

    } finally {
        isLoading.value = false
    }
}

</script>

<style scoped>

.upload-view {
    min-height: 100vh;
    background-color: var(--color-bg-base);
}

.upload-view__hero {
    position: relative;
    overflow: hidden;
    padding: var(--space-14) var(--padding-page-x);
    background-color: var(--color-bg-base);
}

.upload-view__hero-bg {
    position: absolute;
    inset: 0;
    background-image: url('/img/imagem-upload.png');
    background-size: cover;
    background-position: center;
    z-index: 0;
}

.upload-view__hero-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg,
        color-mix(in srgb, var(--color-bg-base) 85%, transparent) 0%,
        color-mix(in srgb, var(--color-bg-base) 60%, transparent) 55%,
        color-mix(in srgb, var(--color-bg-mid) 35%, transparent) 100%);
    z-index: 1;
}

.upload-view__hero-edge {
    position: absolute;
    right: 0;
    bottom: 0;
    left: 0;
    height: 1px;
    background: linear-gradient(90deg,
        color-mix(in srgb, var(--color-gold) 50%, transparent),
        color-mix(in srgb, var(--color-gold) 20%, transparent),
        transparent);
    z-index: 2;
}

.upload-view__hero-content {
    position: relative;
    z-index: 3;
    max-width: var(--max-width);
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
}

.upload-view__hero-title {
    font-family: var(--font-heading);
    font-weight: var(--font-weight-black);
    font-size: var(--font-size-display);
    letter-spacing: var(--letter-spacing-tight);
    line-height: var(--line-height-display);
    color: var(--color-text-primary);
}

.upload-view__hero-title--muted {
    display: block;
    color: var(--color-text-muted);
}

.upload-view__content {
    max-width: var(--max-width);
    margin: 0 auto;
    padding: var(--padding-section) var(--padding-page-x);
}

.upload-view__layout {
    display: grid;
    grid-template-columns: 1.6fr 1fr;
    align-items: start;
    gap: var(--space-8);
}

.upload-view__panel {
    display: flex;
    flex-direction: column;
    gap: var(--space-8);
    padding: var(--padding-card);
    background-color: var(--color-surface-primary);
    border: 1px solid var(--color-border-default);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-card);
}

.upload-view__aside {
    display: flex;
    flex-direction: column;
    gap: var(--space-6);
}

.upload-view__info-card {
    display: flex;
    flex-direction: column;
    gap: var(--space-5);
    padding: var(--padding-card);
    background-color: var(--color-surface-elevated);
    border: 1px solid var(--color-border-default);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-card);
    transition: transform var(--transition-default), border-color var(--transition-default);
}

.upload-view__info-card:hover {
    transform: translateY(-4px);
    border-color: var(--color-border-gold);
}

.upload-view__steps {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    list-style: none;
    margin: 0;
    padding: 0;
}

.upload-view__step {
    display: flex;
    align-items: flex-start;
    gap: var(--space-4);
}

.upload-view__step-index {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background-color: var(--color-gold-dim);
    border: 1px solid var(--color-border-gold);
    border-radius: var(--radius-full);
    color: var(--color-gold);
    font-family: var(--font-mono);
    font-size: var(--font-size-small);
    font-weight: var(--font-weight-bold);
}

.upload-view__step-title {
    color: var(--color-text-primary);
    font-family: var(--font-body);
    font-weight: var(--font-weight-semibold);
    font-size: var(--font-size-body);
}

.upload-view__step-text {
    color: var(--color-text-tertiary);
    font-family: var(--font-body);
    font-size: var(--font-size-small);
    line-height: var(--line-height-body);
}

.upload-view__info-text {
    color: var(--color-text-secondary);
    font-family: var(--font-body);
    font-size: var(--font-size-small);
    line-height: var(--line-height-body);
}

.upload-view__dropzone {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-4);
    padding: var(--space-14) var(--space-8);
    background-color: var(--color-bg-deep);
    border: 1px dashed var(--color-border-default);
    border-radius: var(--radius-xl);
    text-align: center;
    transition: border-color var(--transition-default), background-color var(--transition-default);
}

.upload-view__dropzone:hover,
.upload-view__dropzone--active {
    border-color: var(--color-border-gold-full);
    background-color: var(--color-gold-dim);
}

.upload-view__dropzone--filled {
    border-style: solid;
    border-color: var(--color-border-teal);
}

.upload-view__file-input {
    position: absolute;
    inset: 0;
    opacity: 0;
    cursor: pointer;
}

.upload-view__dropzone-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 64px;
    height: 64px;
    background-color: var(--color-warning-bg);
    border: 1px solid var(--color-border-gold);
    border-radius: var(--radius-lg);
    color: var(--color-gold);
    transition: background-color var(--transition-default), border-color var(--transition-default), color var(--transition-default);
}

.upload-view__dropzone--filled .upload-view__dropzone-icon {
    background-color: var(--color-success-bg);
    border-color: var(--color-border-teal);
    color: var(--color-teal-light);
}

.upload-view__dropzone-icon svg {
    width: 28px;
    height: 28px;
}

.upload-view__dropzone-title {
    font-family: var(--font-body);
    font-weight: var(--font-weight-bold);
    font-size: var(--font-size-h3);
    color: var(--color-text-primary);
}

.upload-view__dropzone-hint {
    font-family: var(--font-body);
    font-size: var(--font-size-body);
    color: var(--color-text-tertiary);
}

.upload-view__dropzone-link {
    color: var(--color-gold);
    font-weight: var(--font-weight-semibold);
    text-decoration: underline;
}

.upload-view__tags {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
}

.upload-view__tag {
    padding: var(--space-1) var(--space-3);
    background-color: var(--color-surface-elevated);
    border: 1px solid var(--color-border-default);
    border-radius: var(--radius-full);
    color: var(--color-text-tertiary);
    font-family: var(--font-mono);
    font-size: var(--font-size-label);
    letter-spacing: var(--letter-spacing-label);
    text-transform: uppercase;
}

.upload-view__classification {
    display: flex;
    flex-direction: column;
    gap: var(--space-5);
    padding-top: var(--space-6);
    border-top: 1px solid var(--color-border-subtle);
}

.upload-view__section-label {
    display: inline-flex;
    align-items: center;
    gap: var(--space-3);
    font-family: var(--font-mono);
    font-size: var(--font-size-label);
    letter-spacing: var(--letter-spacing-label);
    text-transform: uppercase;
    color: var(--color-gold);
}

.upload-view__section-label-line {
    width: 20px;
    height: 1px;
    background-color: var(--color-gold);
}

.upload-view__field {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
}

.upload-view__label {
    font-family: var(--font-mono);
    font-size: var(--font-size-label);
    letter-spacing: var(--letter-spacing-label);
    text-transform: uppercase;
    color: var(--color-text-tertiary);
}

.upload-view__select-wrap {
    position: relative;
    display: flex;
    align-items: center;
}

.upload-view__select {
    width: 100%;
    appearance: none;
    -webkit-appearance: none;
    padding: var(--space-3) var(--space-10) var(--space-3) var(--space-4);
    background-color: var(--color-bg-deep);
    border: 1px solid var(--color-border-default);
    border-radius: var(--radius-sm);
    color: var(--color-text-primary);
    font-family: var(--font-body);
    font-size: var(--font-size-body);
    cursor: pointer;
    transition: border-color var(--transition-default);
}

.upload-view__select:focus {
    outline: none;
    border-color: var(--color-border-gold-full);
}

.upload-view__select:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.upload-view__select-chevron {
    position: absolute;
    right: var(--space-4);
    width: 14px;
    height: 14px;
    color: var(--color-text-tertiary);
    pointer-events: none;
}

.upload-view__progress {
    position: relative;
    display: flex;
    align-items: center;
    gap: var(--space-3);
    background-color: var(--color-bg-deep);
    border-radius: var(--radius-sm);
    padding: var(--space-2) var(--space-4);
    overflow: hidden;
}

.upload-view__progress-bar {
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    background-color: var(--color-gold);
    border-radius: var(--radius-sm);
    transition: width var(--transition-slow);
    opacity: 0.3;
}

.upload-view__progress-label {
    position: relative;
    color: var(--color-text-primary);
    font-family: var(--font-mono);
    font-size: var(--font-size-small);
    font-weight: var(--font-weight-semibold);
}

.upload-view__error {
    color: var(--color-danger);
    font-family: var(--font-body);
    font-size: var(--font-size-small);
    background-color: var(--color-danger-bg);
    border: 1px solid var(--color-danger-border);
    border-radius: var(--radius-sm);
    padding: var(--space-2) var(--space-4);
}

.upload-view__submit-btn {
    width: 100%;
    padding: var(--space-4) var(--space-6);
    background-color: var(--color-gold);
    border: none;
    border-radius: var(--radius-sm);
    color: var(--color-bg-deep);
    font-family: var(--font-body);
    font-weight: var(--font-weight-black);
    font-size: var(--font-size-body);
    cursor: pointer;
    transition: background-color var(--transition-default);
}

.upload-view__submit-btn:hover:not(:disabled) {
    background-color: var(--color-gold-hover);
}

.upload-view__submit-btn:disabled {
    background-color: var(--color-surface-elevated);
    color: var(--color-text-tertiary);
    cursor: not-allowed;
}

.upload-view__empty {
    padding: var(--space-8);
    text-align: center;
    color: var(--color-text-tertiary);
    font-family: var(--font-mono);
    font-size: var(--font-size-label);
    letter-spacing: var(--letter-spacing-mono);
    text-transform: uppercase;
}

@media (max-width: 1024px) {

    .upload-view__layout {
        grid-template-columns: 1fr;
    }

}

@media (max-width: 640px) {

    .upload-view__panel,
    .upload-view__info-card {
        padding: var(--space-5);
        gap: var(--space-6);
    }

    .upload-view__dropzone {
        padding: var(--space-8) var(--space-4);
    }

}

</style>
