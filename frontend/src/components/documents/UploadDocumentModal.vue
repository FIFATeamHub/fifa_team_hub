<template>
    <div v-if="isOpen" class="upload-modal-overlay" @click.self="onClose">
        <div class="upload-modal">

            <header class="upload-modal__header">
                <h2 class="upload-modal__title">Enviar Documento</h2>
            </header>

            <div
                class="upload-modal__dropzone"
                :class="{
                    'upload-modal__dropzone--active': isDragging,
                    'upload-modal__dropzone--filled': !!selectedFile
                }"
                @dragover.prevent="isDragging = true"
                @dragleave.prevent="isDragging = false"
                @drop.prevent="handleDrop"
            >
                <span class="upload-modal__dropzone-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 15V4m0 0-4 4m4-4 4 4" stroke-linecap="round" stroke-linejoin="round" />
                        <path d="M4 15v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                </span>

                <p class="upload-modal__dropzone-title">
                    {{ selectedFile ? selectedFile.name : 'Arraste arquivos aqui' }}
                </p>

                <p v-if="!selectedFile" class="upload-modal__dropzone-hint">
                    ou <span class="upload-modal__dropzone-link">clique para selecionar</span> do dispositivo
                </p>
                <p v-else class="upload-modal__dropzone-hint">
                    Clique para selecionar outro arquivo
                </p>

                <div class="upload-modal__tags">
                    <span class="upload-modal__tag">PDF</span>
                    <span class="upload-modal__tag">DOCX</span>
                    <span class="upload-modal__tag">JPG</span>
                    <span class="upload-modal__tag">PNG</span>
                    <span class="upload-modal__tag">máx. 10MB</span>
                </div>

                <input
                    type="file"
                    class="upload-modal__file-input"
                    accept=".pdf,.jpg,.jpeg,.png,.docx"
                    :disabled="isLoading"
                    @change="handleFileChange"
                />
            </div>

            <div class="upload-modal__field">
                <label class="upload-modal__label" for="upload-modal-category">Categoria</label>
                <div class="upload-modal__select-wrap">
                    <select
                        id="upload-modal-category"
                        v-model="selectedType"
                        class="upload-modal__select"
                        :disabled="isLoading || lockType"
                    >
                        <option value="" disabled>Selecione uma categoria</option>
                        <option value="CONVOCADO">Convocação</option>
                        <option value="PASSPORT">Passaporte</option>
                        <option value="LAUDO_MEDICO">Laudo Médico</option>
                        <option value="RELATORIO_TATICO">Relatório Tático</option>
                        <option value="ESQUEMA_JOGADAS">Esquema de Jogadas</option>
                    </select>
                    <svg class="upload-modal__select-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M6 9l6 6 6-6" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                </div>
            </div>

            <div v-if="isLoading" class="upload-modal__progress">
                <div class="upload-modal__progress-bar" :style="{ width: uploadProgress + '%' }"></div>
                <span class="upload-modal__progress-label">{{ uploadProgress }}%</span>
            </div>

            <p v-if="errorMessage" class="upload-modal__error">{{ errorMessage }}</p>

            <div class="upload-modal__actions">
                <button @click="onClose" :disabled="isLoading" class="upload-modal__btn upload-modal__btn--secondary">
                    Cancelar
                </button>
                <button @click="handleSubmit" :disabled="!isFormValid || isLoading" class="upload-modal__btn upload-modal__btn--primary">
                    {{ isLoading ? 'Enviando...' : 'Enviar' }}
                </button>
            </div>

        </div>
    </div>
</template>
<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { uploadDocument } from '@/services/documentService.js'

// Props com tipagem correta para TypeScript
const props = defineProps<{
  isOpen: boolean
  onClose?: () => void
  onSuccess?: (doc: unknown) => void
  preselectedType?: string
}>()

// Se o modal for aberto a partir de um item do Painel de Pendências, o tipo
// já vem definido e o select fica travado para evitar que o Jogador envie
// um tipo de documento fora do que está pendente para ele.
const lockType = computed(() => Boolean(props.preselectedType))

const selectedFile     = ref<File | null>(null)
const selectedType     = ref(props.preselectedType ?? '')
const isDragging       = ref(false)
const uploadProgress   = ref(0)
const isLoading        = ref(false)
const errorMessage     = ref('')

watch(
  () => props.preselectedType,
  (novoTipo) => {
    selectedType.value = novoTipo ?? ''
  }
)

watch(
  () => props.isOpen,
  (aberto) => {
    if (aberto) {
      selectedFile.value = null
      errorMessage.value = ''
      uploadProgress.value = 0
      selectedType.value = props.preselectedType ?? ''
    }
  }
)

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

// "event: Event" diz ao TypeScript qual é o tipo do parâmetro
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

  isLoading.value     = true
  errorMessage.value  = ''
  uploadProgress.value = 0

  const formData = new FormData()
  formData.append('file', selectedFile.value)   // agora TypeScript sabe que não é null
  formData.append('doc_type', selectedType.value)

  try {
    const resposta = await uploadDocument(formData, (progressEvent: { loaded: number; total: number }) => {
      uploadProgress.value = Math.round(
        (progressEvent.loaded * 100) / progressEvent.total
      )
    })

    props.onSuccess?.(resposta.data)   // ?. evita erro se props for undefined
    props.onClose?.()

  } catch (erro) {
    // TypeScript não sabe o tipo do erro no catch — fazemos um cast
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

.upload-modal-overlay {
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--space-6);
    background-color: color-mix(in srgb, var(--color-bg-deep) 80%, transparent);
    z-index: var(--z-modal);
}

.upload-modal {
    display: flex;
    flex-direction: column;
    gap: var(--space-6);
    width: 100%;
    max-width: 30rem;
    max-height: 90vh;
    overflow-y: auto;
    padding: var(--padding-card);
    background-color: var(--color-surface-primary);
    border: 1px solid var(--color-border-default);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-deep);
}

.upload-modal__header {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
}

.upload-modal__title {
    font-family: var(--font-heading);
    font-weight: var(--font-weight-black);
    font-size: var(--font-size-h3);
    letter-spacing: var(--letter-spacing-heading);
    color: var(--color-text-primary);
}

.upload-modal__dropzone {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-3);
    padding: var(--space-8) var(--space-4);
    background-color: var(--color-bg-deep);
    border: 1px dashed var(--color-border-default);
    border-radius: var(--radius-xl);
    text-align: center;
    transition: border-color var(--transition-default), background-color var(--transition-default);
}

.upload-modal__dropzone:hover,
.upload-modal__dropzone--active {
    border-color: var(--color-border-gold-full);
    background-color: var(--color-gold-dim);
}

.upload-modal__dropzone--filled {
    border-style: solid;
    border-color: var(--color-border-teal);
}

.upload-modal__file-input {
    position: absolute;
    inset: 0;
    opacity: 0;
    cursor: pointer;
}

.upload-modal__dropzone-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 52px;
    height: 52px;
    background-color: var(--color-warning-bg);
    border: 1px solid var(--color-border-gold);
    border-radius: var(--radius-lg);
    color: var(--color-gold);
    transition: background-color var(--transition-default), border-color var(--transition-default), color var(--transition-default);
}

.upload-modal__dropzone--filled .upload-modal__dropzone-icon {
    background-color: var(--color-success-bg);
    border-color: var(--color-border-teal);
    color: var(--color-teal-light);
}

.upload-modal__dropzone-icon svg {
    width: 24px;
    height: 24px;
}

.upload-modal__dropzone-title {
    font-family: var(--font-body);
    font-weight: var(--font-weight-bold);
    font-size: var(--font-size-body);
    color: var(--color-text-primary);
}

.upload-modal__dropzone-hint {
    font-family: var(--font-body);
    font-size: var(--font-size-small);
    color: var(--color-text-tertiary);
}

.upload-modal__dropzone-link {
    color: var(--color-gold);
    font-weight: var(--font-weight-semibold);
    text-decoration: underline;
}

.upload-modal__tags {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
}

.upload-modal__tag {
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

.upload-modal__field {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
}

.upload-modal__label {
    font-family: var(--font-mono);
    font-size: var(--font-size-label);
    letter-spacing: var(--letter-spacing-label);
    text-transform: uppercase;
    color: var(--color-text-tertiary);
}

.upload-modal__select-wrap {
    position: relative;
    display: flex;
    align-items: center;
}

.upload-modal__select {
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

.upload-modal__select:focus {
    outline: none;
    border-color: var(--color-border-gold-full);
}

.upload-modal__select:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.upload-modal__select-chevron {
    position: absolute;
    right: var(--space-4);
    width: 14px;
    height: 14px;
    color: var(--color-text-tertiary);
    pointer-events: none;
}

.upload-modal__progress {
    position: relative;
    display: flex;
    align-items: center;
    gap: var(--space-3);
    background-color: var(--color-bg-deep);
    border-radius: var(--radius-sm);
    padding: var(--space-2) var(--space-4);
    overflow: hidden;
}

.upload-modal__progress-bar {
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    background-color: var(--color-gold);
    border-radius: var(--radius-sm);
    transition: width var(--transition-slow);
    opacity: 0.3;
}

.upload-modal__progress-label {
    position: relative;
    color: var(--color-text-primary);
    font-family: var(--font-mono);
    font-size: var(--font-size-small);
    font-weight: var(--font-weight-semibold);
}

.upload-modal__error {
    color: var(--color-danger);
    font-family: var(--font-body);
    font-size: var(--font-size-small);
    background-color: var(--color-danger-bg);
    border: 1px solid var(--color-danger-border);
    border-radius: var(--radius-sm);
    padding: var(--space-2) var(--space-4);
}

.upload-modal__actions {
    display: flex;
    justify-content: flex-end;
    gap: var(--space-3);
}

.upload-modal__btn {
    padding: var(--space-3) var(--space-6);
    border-radius: var(--radius-sm);
    font-family: var(--font-body);
    font-size: var(--font-size-body);
    cursor: pointer;
    transition: background-color var(--transition-default), border-color var(--transition-default), color var(--transition-default);
}

.upload-modal__btn--secondary {
    background: none;
    border: 1px solid var(--color-border-default);
    color: var(--color-text-secondary);
    font-weight: var(--font-weight-semibold);
}

.upload-modal__btn--secondary:hover:not(:disabled) {
    border-color: var(--color-border-teal);
    color: var(--color-teal-light);
}

.upload-modal__btn--primary {
    background-color: var(--color-gold);
    border: none;
    color: var(--color-bg-deep);
    font-weight: var(--font-weight-black);
}

.upload-modal__btn--primary:hover:not(:disabled) {
    background-color: var(--color-gold-hover);
}

.upload-modal__btn--primary:disabled {
    background-color: var(--color-surface-elevated);
    color: var(--color-text-tertiary);
}

.upload-modal__btn:disabled {
    cursor: not-allowed;
    opacity: 0.6;
}

@media (max-width: 480px) {

    .upload-modal {
        padding: var(--space-5);
        gap: var(--space-5);
    }

    .upload-modal__dropzone {
        padding: var(--space-6) var(--space-3);
    }

}

</style>
