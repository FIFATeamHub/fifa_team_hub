<template>
    <div v-if="isOpen" class="modal-overlay" @click.self="onClose">
        <div class="modal-box">
            <h2 class="modal-titulo">Enviar Documento</h2>

            <!-- Area da upload-->
            <div class="campo">
                <label>Selecione o arquivo</label>
                <input 
                type="file" 
                accept=".pdf,.jpg,.jpeg,.png,.docx"
                :disabled="isLoading"
                @change="handleFileChange" 
                />
            </div>

            <!-- Campo: Tipo de documento-->
            <div class="campo">
                <label>Tipo de documento</label>
                <select v-model="selectedType" :disabled="isLoading || lockType">
                    <option value="" disabled>Selecione...</option>
                    <option value="CONVOCADO">Convocação</option>
                    <option value="PASSPORT">Passaporte</option>
                    <option value="LAUDO_MEDICO">Laudo Médico</option>
                    <option value="RELATORIO_TATICO">Relatório Tático</option>
                    <option value="ESQUEMA_JOGADAS">Esquema de Jogadas</option>
                </select>
            </div>

            <!-- Barra de Progresso (só durante o upload)-->
             <div v-if="isLoading" class="progresso-container">
                <div class="progresso-barra" :style="{width: uploadProgress + '%'}"></div>
                <span>{{ uploadProgress }}%</span>
             </div>

             <!-- Mensagem de Erro -->
             <p v-if="errorMessage" class="mensagem-erro">{{ errorMessage }}</p>

             <!-- Botoes -->
              <div class="botoes">
                <button @click="onClose" :disabled="isLoading" class="btn-cancelar">
                Cancelar
                </button>
                <button @click="handleSubmit" :disabled="!isFormValid || isLoading" class="btn-enviar">
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

// "event: Event" diz ao TypeScript qual é o tipo do parâmetro
function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const arquivo = input.files?.[0]
  errorMessage.value = ''

  if (arquivo && arquivo.size > 10 * 1024 * 1024) {
    errorMessage.value = 'O ficheiro excede o limite de 10 MB.'
    selectedFile.value = null
    return
  }

  selectedFile.value = arquivo ?? null
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
/* Fundo escuro que cobre a tela toda */
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
/* A caixa do modal */
.modal-box {
  background-color: var(--color-surface-elevated);
  border: 1px solid var(--color-border-default);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  width: 100%;
  max-width: 480px;
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}
.modal-titulo {
  font-family: var(--font-heading);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
  font-size: var(--font-size-h3);
  letter-spacing: var(--letter-spacing-heading);
}
/* Cada campo do formulário */
.campo {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.campo label {
  font-family: var(--font-mono);
  color: var(--color-text-tertiary);
  font-size: var(--font-size-label);
  letter-spacing: var(--letter-spacing-label);
  text-transform: uppercase;
}
.campo input,
.campo select {
  background-color: var(--color-bg-deep);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border-default);
  border-radius: var(--radius-sm);
  padding: var(--space-3) var(--space-4);
  font-family: var(--font-body);
  font-size: var(--font-size-body);
  outline: none;
  transition: border-color var(--transition-default);
}
.campo select:focus,
.campo input:focus {
  border-color: var(--color-border-gold-full);
}
.campo input:disabled,
.campo select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
/* Barra de progresso */
.progresso-container {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  background-color: var(--color-bg-deep);
  border-radius: var(--radius-sm);
  padding: var(--space-2) var(--space-4);
  overflow: hidden;
  position: relative;
}
.progresso-barra {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background-color: var(--color-gold);
  border-radius: var(--radius-sm);
  transition: width 0.3s ease;
  opacity: 0.3;
}
.progresso-container span {
  position: relative; /* fica na frente da barra */
  color: var(--color-text-primary);
  font-family: var(--font-body);
  font-size: var(--font-size-small);
  font-weight: var(--font-weight-semibold);
}
/* Mensagem de erro */
.mensagem-erro {
  color: var(--color-danger);
  font-family: var(--font-body);
  font-size: var(--font-size-small);
  margin: 0;
  background-color: var(--color-danger-bg);
  border: 1px solid var(--color-danger-border);
  border-radius: var(--radius-sm);
  padding: var(--space-2) var(--space-4);
}
/* Linha dos botões */
.botoes {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  margin-top: var(--space-2);
}
.btn-cancelar,
.btn-enviar {
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-full);
  font-family: var(--font-body);
  font-size: var(--font-size-small);
  font-weight: var(--font-weight-semibold);
  border: 1px solid transparent;
  cursor: pointer;
  transition: opacity var(--transition-default), border-color var(--transition-default);
}
.btn-cancelar {
  background: none;
  border-color: var(--color-border-default);
  color: var(--color-text-secondary);
}
.btn-cancelar:hover:not(:disabled) {
  border-color: var(--color-border-teal);
  color: var(--color-teal-light);
}
.btn-enviar {
  background-color: var(--color-gold);
  border-color: var(--color-gold);
  color: var(--color-bg-deep);
  font-weight: var(--font-weight-black);
}
.btn-enviar:hover:not(:disabled) {
  background-color: var(--color-gold-hover);
  border-color: var(--color-gold-hover);
}
.btn-cancelar:disabled,
.btn-enviar:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>