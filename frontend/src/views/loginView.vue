<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const errorMessage = ref('')

async function handleSubmit() {
  errorMessage.value = ''

  try {
    await authStore.login({ email: email.value, password: password.value })
  } catch (error) {
    if (error.status === 401) {
      errorMessage.value = 'E-mail ou senha incorretos'
    }
  }
}
</script>
<template>
  <form @submit.prevent="handleSubmit">
    <input type="email" v-model="email" required>
    
    <input type="password" v-model="password" required>
    
    <p>{{ errorMessage }}</p>

    <button type="submit">Entrar</button>
  </form>
</template>