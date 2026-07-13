
<template>

    <h2>Criar Conta</h2>

    <div class = "container-form">
        <form @submit.prevent="lidarComCadastro">   
            <div class = "container-campo">
                <label for="nome">Nome:</label>
                <input name = "nome" type="text" v-model ="nome" required>
            </div>
            <div class = "container-campo">
                <label for="email">Email:</label>
                <input name = "email" type="email" v-model ="email" required>
            </div>

            <div class="campo">
                <label>País de residência:</label>
                <select v-model="selection" required>
                    <option value="">Selecione sua seleção</option>

                    <option
                        v-for="item in selections"
                        :key="item.id"
                        :value="item.id"
                    >
                        {{ item.name }}
                    </option>
                </select>
            </div>

            <div class="campo">
                <label>Senha (mínimo 8 caracteres):</label>
                <input type="password" v-model="password" required />
            </div>

            <div class="campo">
                <label>Confirme a Senha:</label>
                <input type="password" v-model="passwordConfirm" required />
            </div>

            <button type="submit">Cadastrar</button>

            <p class="link-login">
                Já tem conta? <RouterLink to="/login">Voltar para o Login</RouterLink>
            </p>

            <p v-if="errorMessage" class="msg-erro">{{ errorMessage }}</p>
            <p v-if="successMessage" class="msg-sucesso">{{ successMessage }}</p>

        </form>

    </div>

</template>





<script setup lang="ts">

import {ref, onMounted} from 'vue'
import {useAuthStore} from '@/stores/auth.js'
import { useRouter , RouterLink } from 'vue-router'
import api from '@/services/api';

const selections = ref([])

onMounted(async () => {
    try {
        const response = await api.get('/api/selection/')
        selections.value = response.data
    } catch (err) {
        console.error(err)
    }
})


const authStore = useAuthStore()
const router = useRouter()

const nome = ref('')
const email = ref('')
const password = ref('')
const passwordConfirm = ref('')
const selection = ref(null)

const errorMessage = ref('')
const successMessage = ref('')

const lidarComCadastro = async() => {

    errorMessage.value = ''
    successMessage.value = ''

    if(password.value.length < 8){
        errorMessage.value = 'A senha deve conter no mínimo 8 dígitos'
        return 
    }

    if(password.value !== passwordConfirm.value){
        errorMessage.value = 'As senhas digitadas são diferentes'
        return 
    }

    try {

        await authStore.register({
            nome: nome.value,
            email: email.value,
            password: password.value,
            selection: selection.value
        })

        successMessage.value = 'Solicitação enviada ao auditor'

        nome.value = ''
        email.value = ''
        password.value = ''
        passwordConfirm.value = ''
        selection.value = null

        setTimeout(() => {
            router.push('/login')
        }, 2000)

    }
    catch (err) {
    const error = err as { message?: string }
    if (error.message) {
      errorMessage.value = error.message
        } else {
        errorMessage.value = 'Ocorreu um erro ao registrar a conta.'
        }
    }
}

</script>





<style scoped>

    h2{
        margin-top: 10px;
    }

</style>