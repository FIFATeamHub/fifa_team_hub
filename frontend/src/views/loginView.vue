
<template>
  <form @submit.prevent="handleSubmit">
    <input type="email" v-model="email" required>
    
    <input type="password" v-model="password" required>
    
    <p>{{ errorMessage }}</p>

    <button type="submit">Entrar</button>
  </form>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'      

const authStore = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const errorMessage = ref('')

async function handleSubmit() {
  errorMessage.value = ''

  try {
    
    await authStore.login({ email: email.value, password: password.value })
    router.push('/dashboard')

    } catch (error) {
    if (error.status === 401) {
      errorMessage.value = 'E-mail ou senha incorretos'
    } else {
      errorMessage.value = 'Ocorreu um erro no servidor. Verifique os dados e tente novamente.'
    }
    console.error(error) // Isso imprime o erro no F12 para você debugar!
  }

}
</script>