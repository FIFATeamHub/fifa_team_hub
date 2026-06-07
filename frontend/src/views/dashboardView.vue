<template>
  <div class="conteudo-container">
      
      <header class="dashboard-header">
        <div class="usuario-info">
          <span>Bem-vindo, <strong>{{ authStore.user?.full_name || 'Usuário' }}</strong></span>
        </div>
        
        <button @click="efetuarLogout" class="botao-sair">Sair do Sistema</button>
      </header>

      <main class="conteudo-principal">

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

      </main>

    </div>
</template>


<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import protectedContent from '@/components/protectedContent.vue'

const authStore = useAuthStore()
const router = useRouter()

const efetuarLogout = () => {
  authStore.logout()
  router.push('/login')
}

onMounted(async () => {
  if (authStore.token && !authStore.user) {
    try {
      await authStore.fetchMe()
    } catch (err) {
      authStore.logout()
      router.push('/login')
    }
  }
})
</script>