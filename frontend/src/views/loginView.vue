
<<<<<<< HEAD
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
    }
  }
}
</script>
=======

<template>
    <div class = "page">

        <LoginForm/>

        <!-- <p>teste</p> -->

    </div>

</template>

<script setup>

import LoginForm from '@/components/loginForm.vue';

</script>

<style scoped>

    :global(html),
    :global(body),
    :global(#app) {
        margin: 0;
        padding: 0; 
        box-sizing: border-box;
        
    }

    .page{
        background-color: #061c42;
    }


</style>
>>>>>>> e6e1e96 (fetch : logica e página de registros / estilizando algumas tela / organizando arquivos em componentes)
