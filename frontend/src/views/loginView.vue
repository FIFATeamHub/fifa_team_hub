<template>
  <div class="page">
    <LoginForm />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import LoginForm from '@/components/loginForm.vue'

const errorMessage = ref('')

const handleLogin = async () => {
  try {
  } catch (error: any) {
    if (error.status === 401) {
      errorMessage.value = 'E-mail ou senha incorretos'
    } else {
      errorMessage.value = 'Ocorreu um erro no servidor. Verifique os dados e tente novamente.'
    }
    console.error(error)
  }
}
</script>

<style scoped>
:global(html),
:global(body),
:global(#app) {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.page {
  background-color: #061c42;
  min-height: 100vh;
}
</style>