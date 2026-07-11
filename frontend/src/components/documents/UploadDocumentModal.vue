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
                <select v-model="selectedType" :disabled="isLoading">
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
import { ref, computed } from 'vue'
import { uploadDocument } from '@/services/documentService.js'

// Props com tipagem correta para TypeScript
const props = defineProps<{
  isOpen: boolean
  onClose?: () => void
  onSuccess?: (doc: unknown) => void
}>()

const selectedFile     = ref<File | null>(null)
const selectedType     = ref('')
const uploadProgress   = ref(0)
const isLoading        = ref(false)
const errorMessage     = ref('')

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
  formData.append('file', selectedFile.value)
  formData.append('doc_type', selectedType.value)

  try {
    const resposta = await uploadDocument(formData, (progressEvent: { loaded: number; total: number }) => {
      uploadProgress.value = Math.round(
        (progressEvent.loaded * 100) / progressEvent.total
      )
    })

    props.onSuccess?.(resposta.data)
    props.onClose?.()

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
/* A caixa branca do modal */
.modal-box {
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 2rem;
  width: 100%;
  max-width: 480px;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}
.modal-titulo {
  color: #f1f5f9;
  margin: 0;
  font-size: 1.25rem;
}
/* Cada campo do formulário */
.campo {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.campo label {
  color: #94a3b8;
  font-size: 0.875rem;
}
.campo input,
.campo select {
  background-color: #0f172a;
  color: #f1f5f9;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 0.6rem 0.8rem;
  font-size: 0.95rem;
  outline: none;
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
  gap: 0.75rem;
  background-color: #0f172a;
  border-radius: 8px;
  padding: 0.5rem 0.8rem;
  overflow: hidden;
  position: relative;
}
.progresso-barra {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background-color: #3b82f6;
  border-radius: 8px;
  transition: width 0.3s ease;
  opacity: 0.3;
}
.progresso-container span {
  position: relative; /* fica na frente da barra */
  color: #f1f5f9;
  font-size: 0.875rem;
  font-weight: 600;
}
/* Mensagem de erro */
.mensagem-erro {
  color: #f87171;
  font-size: 0.875rem;
  margin: 0;
  background-color: rgba(248, 113, 113, 0.1);
  border-radius: 6px;
  padding: 0.5rem 0.8rem;
}
/* Linha dos botões */
.botoes {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
}
.btn-cancelar,
.btn-enviar {
  padding: 0.55rem 1.25rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: opacity 0.2s;
}
.btn-cancelar {
  background-color: #334155;
  color: #cbd5e1;
}
.btn-enviar {
  background-color: #3b82f6;
  color: white;
}
.btn-cancelar:disabled,
.btn-enviar:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>