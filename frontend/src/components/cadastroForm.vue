
<template>

    <div class="register-page">
        <div class="register-card">

            <header class="register-card__header">
                <h2 class="register-card__title">Solicitar <span class="register-card__title-accent">acesso</span></h2>
                <p class="register-card__subtitle">Preencha para solicitar acesso</p>
            </header>

            <div class="register-card__body">

                <form class="register-card__form" @submit.prevent="lidarComCadastro">

                    <div class="form-field">
                        <label for="nome" class="form-field__label">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M20 21a8 8 0 0 0-16 0" />
                                <circle cx="12" cy="7" r="4" />
                            </svg>
                            Nome completo
                        </label>
                        <input id="nome" name="nome" type="text" v-model="nome" required class="form-field__input" placeholder="Seu nome completo">
                    </div>

                    <div class="form-field">
                        <label for="email" class="form-field__label">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M3 6h18v12H3z" />
                                <path d="M3 7l9 6 9-6" />
                            </svg>
                            E-mail
                        </label>
                        <input id="email" name="email" type="email" v-model="email" required class="form-field__input" placeholder="seu@email.com">
                    </div>

                    <div class="form-field">
                        <label for="selection" class="form-field__label">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M12 21s-7-6.1-7-11a7 7 0 0 1 14 0c0 4.9-7 11-7 11z" />
                                <circle cx="12" cy="10" r="2.5" />
                            </svg>
                            País de residência
                        </label>
                        <div class="form-field__select-wrapper">
                            <select id="selection" v-model="selection" required class="form-field__input form-field__select">
                                <option value="" disabled selected>Selecione seu país</option>

                                <option
                                    v-for="item in selections"
                                    :key="item.id"
                                    :value="item.id"
                                >
                                    {{ item.name }}
                                </option>
                            </select>
                        </div>
                    </div>

                    <div class="form-field">
                        <label for="password" class="form-field__label">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="5" y="11" width="14" height="9" rx="1" />
                                <path d="M8 11V7a4 4 0 0 1 8 0v4" />
                            </svg>
                            Senha
                        </label>
                        <input id="password" name="password" type="password" v-model="password" required class="form-field__input">
                        <span class="form-field__hint">Mínimo de 8 caracteres</span>
                    </div>

                    <div class="form-field">
                        <label for="passwordConfirm" class="form-field__label">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="5" y="11" width="14" height="9" rx="1" />
                                <path d="M8 11V7a4 4 0 0 1 8 0v4" />
                            </svg>
                            Confirmar senha
                        </label>
                        <input id="passwordConfirm" name="passwordConfirm" type="password" v-model="passwordConfirm" required class="form-field__input">
                    </div>

                    <p v-if="errorMessage" class="register-card__error">{{ errorMessage }}</p>
                    <p v-if="successMessage" class="register-card__success">{{ successMessage }}</p>

                    <button type="submit" class="register-card__submit">
                        Solicitar acesso
                    </button>
                </form>

                <div class="register-card__divider">
                    <span class="register-card__divider-line"></span>
                    <RouterLink to="/login" class="register-card__divider-link">Voltar ao login</RouterLink>
                    <span class="register-card__divider-line"></span>
                </div>

            </div>

        </div>
    </div>

</template>





<script setup lang="ts">

import {ref, onMounted} from 'vue'
import {useAuthStore} from '@/stores/auth.js'
import { useRouter , RouterLink } from 'vue-router'
import api from '@/services/api';

interface Selection {
  id: string
  name: string
  code: string
}

const selections = ref<Selection[]>([])

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

        successMessage.value = 'Cadastro realizado com sucesso'

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

.register-page {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    min-height: 100%;
    padding: var(--padding-page-x);
}

.register-card {
    width: 100%;
    max-width: 24rem;
    display: flex;
    flex-direction: column;
    gap: var(--space-6);
    padding: var(--space-8) 0;
}

.register-card__header {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
}

.register-card__title {
    font-family: var(--font-heading);
    font-weight: var(--font-weight-black);
    font-size: calc(var(--font-size-h1) * 0.55);
    letter-spacing: var(--letter-spacing-heading);
    line-height: var(--line-height-heading);
    color: var(--color-text-primary);
}

.register-card__title-accent {
    color: var(--color-gold);
}

.register-card__subtitle {
    font-family: var(--font-mono);
    font-size: var(--font-size-label);
    letter-spacing: var(--letter-spacing-label);
    text-transform: uppercase;
    color: var(--color-text-tertiary);
}

.register-card__body {
    display: flex;
    flex-direction: column;
    gap: var(--space-6);
}

.register-card__form {
    display: flex;
    flex-direction: column;
    gap: var(--space-5);
}

.form-field {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
}

.form-field__label {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    font-family: var(--font-mono);
    font-size: var(--font-size-label);
    letter-spacing: var(--letter-spacing-label);
    text-transform: uppercase;
    color: var(--color-text-tertiary);
}

.form-field__label svg {
    width: 14px;
    height: 14px;
    color: var(--color-gold);
    flex-shrink: 0;
}

.form-field__input {
    width: 100%;
    padding: var(--space-3) var(--space-4);
    background-color: transparent;
    border: none;
    border-bottom: 1px solid var(--color-border-default);
    border-radius: 0;
    color: var(--color-text-primary);
    font-family: var(--font-body);
    font-size: var(--font-size-body);
    transition: border-color var(--transition-default);
}

.form-field__input::placeholder {
    color: var(--color-text-muted);
}

.form-field__input:focus {
    outline: none;
    border-color: var(--color-border-gold-full);
}

.form-field__select-wrapper {
    position: relative;
}

.form-field__select {
    appearance: none;
    -webkit-appearance: none;
    cursor: pointer;
    padding-right: var(--space-8);
}

.form-field__select-wrapper::after {
    content: "";
    position: absolute;
    right: var(--space-2);
    top: 50%;
    width: 8px;
    height: 8px;
    border-right: 1px solid var(--color-text-tertiary);
    border-bottom: 1px solid var(--color-text-tertiary);
    transform: translateY(-70%) rotate(45deg);
    pointer-events: none;
}

.form-field__select option {
    background-color: var(--color-surface-input);
    color: var(--color-text-primary);
}

.form-field__hint {
    font-family: var(--font-body);
    font-size: var(--font-size-small);
    color: var(--color-text-muted);
}

.register-card__error {
    padding: var(--space-2) var(--space-3);
    background-color: var(--color-danger-bg);
    border: 1px solid var(--color-danger-border);
    border-radius: var(--radius-sm);
    color: var(--color-danger);
    font-family: var(--font-body);
    font-size: var(--font-size-small);
}

.register-card__success {
    padding: var(--space-2) var(--space-3);
    background-color: var(--color-success-bg);
    border: 1px solid var(--color-success-border);
    border-radius: var(--radius-sm);
    color: var(--color-teal-light);
    font-family: var(--font-body);
    font-size: var(--font-size-small);
}

.register-card__submit {
    margin-top: var(--space-2);
    padding: var(--space-3) var(--space-4);
    background-color: var(--color-gold);
    border: none;
    border-radius: var(--radius-sm);
    color: var(--color-bg-deep);
    font-family: var(--font-body);
    font-weight: var(--font-weight-black);
    font-size: var(--font-size-body);
    cursor: pointer;
    transition: background-color var(--transition-default);
}

.register-card__submit:hover:not(:disabled) {
    background-color: var(--color-gold-hover);
}

.register-card__submit:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.register-card__divider {
    display: flex;
    align-items: center;
    gap: var(--space-3);
}

.register-card__divider-line {
    flex: 1;
    height: 1px;
    background-color: var(--color-border-gold);
}

.register-card__divider-link {
    white-space: nowrap;
    font-family: var(--font-mono);
    font-size: var(--font-size-label);
    letter-spacing: var(--letter-spacing-mono);
    text-transform: uppercase;
    color: var(--color-text-secondary);
    transition: color var(--transition-default);
}

.register-card__divider-link:hover {
    color: var(--color-teal-light);
}

@media (max-width: 480px) {
    .register-card {
        gap: var(--space-4);
        padding: var(--space-6) 0;
    }

    .register-card__body {
        gap: var(--space-4);
    }
}

</style>
