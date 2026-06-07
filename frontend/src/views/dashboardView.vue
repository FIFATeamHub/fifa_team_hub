<template>
  <div class="conteudo-container">
      
      <header class="dashboard-header">
        <div class="usuario-info">
          <span>Bem-vindo, <strong>{{ authStore.user?.full_name || 'Usuário' }}</strong></span>
        </div>
        
        <button @click="efetuarLogout" class="botao-sair">Sair do Sistema</button>
      </header>

      <main class="conteudo-principal">
        <div class="card-alerta-vazio">
          <h3>Área de Conteúdo Vazia</h3>
          <p>Esta seção será preenchida com gráficos e tabelas de dados nas próximas entregas semanais.</p>
        </div>
      </main>

    </div>
</template>


<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

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