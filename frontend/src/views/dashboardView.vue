<template>
  <div class="conteudo-container">
      
      <header class="dashboard-header">
        <div class="usuario-info">
          <span>Bem-vindo, <strong>{{ authStore.user?.full_name || 'Usuário' }}</strong></span>
        </div>
        
        <button @click="efetuarLogout" class="botao-sair">Sair do Sistema</button>
      </header>

      <main class="conteudo-principal">

        <DocumentsList />

        <protectedContent permission="view:logs">

          <div class="card-alerta-vazio">
            <h3>Logs da Auditoria</h3>
            <p>Seção exclusiva do auditor</p>
          </div>

        </protectedContent>

        <protectedContent permission="register:players">

          <div class="card-alerta-vazio">
            <h3>Registro de Jogadores</h3>
            <p>Seção de registro de jogadores.</p>
          </div>
          
        </protectedContent>
        
        <protectedContent permission="view:tactics">

          <div class="card-alerta-vazio">
            <h3>Nossas táticas</h3>
            <p>Seção de táticas do time</p>
          </div>

        </protectedContent>

        <protectedContent permission="edit:tactics">

          <div class="card-alerta-vazio">
            <h3>Editar nossas táticas</h3>
            <p>Seção de edição das táticas do time</p>
          </div>

        </protectedContent>

        <protectedContent permission="upload:med_docs">

          <div class="card-alerta-vazio">
            <h3>Área de Upload - Médico</h3>
            <p>Seção de upload de documentos médicos</p>
          </div>

        </protectedContent>

        <protectedContent permission="view:med_docs">

          <div class="card-alerta-vazio">
            <h3>Área de Documentos - Médico</h3>
            <p>Seção de visualização de documentos médicos</p>
          </div>

        </protectedContent>

        <protectedContent permission="view:bureaucratic">

          <div class="card-alerta-vazio">
            <h3>Área Burocrática</h3>
            <p>Seção de visualização de burocráticos</p>
          </div>

        </protectedContent>
                <!-- Botão visível apenas para TECHNICAL_STAFF -->
        <div v-if="can('upload:documents')" class="secao-upload">
          <button @click="isModalOpen = true" class="btn-upload">
            📄 Enviar Documento
          </button>

          <!-- Lista de documentos enviados nessa sessão -->
          <div v-if="documentos.length > 0" class="lista-documentos">
            <h3>Documentos enviados</h3>
            <ul>
              <li v-for="doc in documentos" :key="doc.id">
                <span>{{ doc.filename }}</span>
                <span class="doc-tipo">{{ doc.type }}</span>
              </li>
            </ul>
          </div>
        </div>

      </main>

    </div>
        <!-- Modal de Upload (renderizado aqui, controlado pelo isModalOpen) -->
    <UploadDocumentModal
      :isOpen="isModalOpen"
      :onClose="() => isModalOpen = false"
      :onSuccess="aoReceberDocumento"
    />
</template>


<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useRouter } from 'vue-router'
import protectedContent from '@/components/protectedContent.vue'
import UploadDocumentModal from '@/components/documents/UploadDocumentModal.vue'
import { usePermissions } from '@/composables/usePermissions'
import DocumentsList from '@/components/documents/documentsList.vue'

const authStore = useAuthStore()
const router    = useRouter()
const { can }   = usePermissions()

// --- Estado local do Dashboard ---
interface Documento {
  id: string
  filename: string
  type: string
}
const isModalOpen = ref(false)
const documentos  = ref<Documento[]>([])

const efetuarLogout = () => {
  authStore.logout()
  router.push('/login')
}

// Chamada pelo modal ao completar upload com sucesso
function aoReceberDocumento(novoDoc: unknown) {
  documentos.value.unshift(novoDoc as Documento)
}

onMounted(async () => {
  if (authStore.token && !authStore.user) {
    try {
      await authStore.fetchMe()
    } catch {
      authStore.logout()
      router.push('/login')
    }
  }
})
</script>
