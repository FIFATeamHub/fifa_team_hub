
<template>
    <div class = "container-page">

        <h1>Login</h1>


        <div class = "container-form">
            <form @submit.prevent="handleSubmit">
                <label for = "email">Email:</label>
                <input name = "email" type="email" v-model="email" required>

                <label for = "password">Senha:</label>
                <input name = "password" type="password" v-model="password" required>
                
                <p>{{ errorMessage }}</p>

                <button type="submit" :disabled="loading">
                    {{ loading ? 'Loading...' : 'Entrar' }}
                </button>
            </form>

            <p id = "#cadastro">
                Ainda não possui conta? : <RouterLink to="/cadastro">Cadastre-se</RouterLink>
            </p>
        </div>
    </div>


</template>





<script setup lang="ts">

import { ref } from 'vue'
<<<<<<< HEAD
 
import { useAuthStore } from '../stores/auth'
=======
import { useAuthStore } from '@/stores/auth.js'
>>>>>>> main
import { RouterLink } from 'vue-router'      

const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const errorMessage = ref('')
const loading = ref(false)

async function handleSubmit() {
  errorMessage.value = ''
    loading.value = true

  try {
    
    await authStore.login({ email: email.value, password: password.value })
<<<<<<< HEAD
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } catch (error: any) {
=======

  } catch (err) {
    const error = err as { status?: number }
>>>>>>> main
    if (error.status === 401) {
      errorMessage.value = 'E-mail ou senha incorretos'
    }
    } finally {
        loading.value = false
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



    .container-page{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 420px;
        width: 100%;
    }

    .container-page h1{
        margin-top: 130px;
        color: #F3F4F6;
    }

    .container-form{
        padding: 70px;
        display: flex;
        flex-direction: column;
        background-color: #b39532;
        border-radius: 10px;


    }

    .container-form label{
        color: #E2E8F0;
        display: block;
        margin-bottom: 10px;

    }

    .container-form p{
        color: white;
        display: block;

    }

    .container-form button:disabled {
        opacity: 0.7;
        cursor: not-allowed;
    }

    .container-form input{
        background-color: #E2E8F0;;
        display: block;
        border-radius: 1px;
        border-color: #121E2B;

    }


</style>