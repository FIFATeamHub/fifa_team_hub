
<template>
    <div class="login-page">
        <div class="login-card">

            <header class="login-card__header">
                <span class="login-card__eyebrow">Login</span>
            </header>

            <div class="login-card__body">
                <h2 class="login-card__title">Bem-vindo de volta!</h2>
                <p class="login-card__subtitle">Entre com suas credenciais</p>

                <form class="login-card__form" @submit.prevent="handleSubmit">
                    <div class="form-field">
                        <label for="email" class="form-field__label">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M3 6h18v12H3z" />
                                <path d="M3 7l9 6 9-6" />
                            </svg>
                            E-mail
                        </label>
                        <input id="email" name="email" type="email" v-model="email" required class="form-field__input">
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
                    </div>

                    <p v-if="errorMessage" class="login-card__error">{{ errorMessage }}</p>

                    <button type="submit" :disabled="loading" class="login-card__submit">
                        {{ loading ? 'Loading...' : 'Entrar' }}
                    </button>
                </form>

                <div class="login-card__divider">
                    <span class="login-card__divider-line"></span>
                    <RouterLink to="/cadastro" class="login-card__divider-link">Solicitar cadastro</RouterLink>
                    <span class="login-card__divider-line"></span>
                </div>
            </div>

        </div>
    </div>
</template>





<script setup lang="ts">

import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
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

  } catch (err) {
    const error = err as { status?: number }
    if (error.status === 401) {
      errorMessage.value = 'E-mail ou senha incorretos'
    }
    } finally {
        loading.value = false
  }
}
</script>




<style scoped>

.login-page {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    min-height: 100vh;
    padding: var(--padding-page-x);
}

.login-card {
    width: 100%;
    max-width: 26rem;
    background-color: var(--color-surface-primary);
    border: 1px solid var(--color-border-gold);
    border-radius: var(--radius-2xl);
    box-shadow: var(--shadow-card);
    overflow: hidden;
    transition: transform var(--transition-default), border-color var(--transition-default);
}

.login-card:hover {
    transform: translateY(-4px);
    border-color: var(--color-border-gold-full);
}

.login-card__header {
    padding: var(--space-5) var(--space-8);
    background-color: var(--color-surface-elevated);
    border-bottom: 1px solid var(--color-border-default);
    text-align: center;
}

.login-card__eyebrow {
    font-family: var(--font-mono);
    font-size: var(--font-size-h3);
    font-weight: var(--font-weight-bold);
    letter-spacing: var(--letter-spacing-label);
    text-transform: uppercase;
    color: var(--color-gold);
}

.login-card__body {
    display: flex;
    flex-direction: column;
    gap: var(--space-6);
    padding: var(--space-8);
}

.login-card__title {
    font-family: var(--font-heading);
    font-weight: var(--font-weight-black);
    letter-spacing: var(--letter-spacing-heading);
    color: var(--color-text-primary);
    text-align: center;
}

.login-card__subtitle {
    margin-top: calc(var(--space-2) * -1);
    font-family: var(--font-mono);
    font-size: var(--font-size-label);
    letter-spacing: var(--letter-spacing-mono);
    text-transform: uppercase;
    color: var(--color-text-tertiary);
    text-align: center;
}

.login-card__form {
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
    font-family: var(--font-body);
    font-weight: var(--font-weight-semibold);
    font-size: var(--font-size-small);
    color: var(--color-text-secondary);
}

.form-field__label svg {
    width: 14px;
    height: 14px;
    color: var(--color-gold);
}

.form-field__input {
    width: 100%;
    padding: var(--space-3) var(--space-4);
    background-color: var(--color-surface-input);
    border: 1px solid var(--color-border-default);
    border-radius: var(--radius-sm);
    color: var(--color-text-primary);
    font-family: var(--font-body);
    font-size: var(--font-size-body);
    transition: border-color var(--transition-default);
}

.form-field__input:focus {
    outline: none;
    border-color: var(--color-border-gold);
}

.login-card__error {
    padding: var(--space-2) var(--space-3);
    background-color: var(--color-danger-bg);
    border: 1px solid var(--color-danger-border);
    border-radius: var(--radius-sm);
    color: var(--color-danger);
    font-family: var(--font-body);
    font-size: var(--font-size-small);
}

.login-card__submit {
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

.login-card__submit:hover:not(:disabled) {
    background-color: var(--color-gold-hover);
}

.login-card__submit:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.login-card__divider {
    display: flex;
    align-items: center;
    gap: var(--space-3);
}

.login-card__divider-line {
    flex: 1;
    height: 1px;
    background-color: var(--color-border-gold);
}

.login-card__divider-link {
    white-space: nowrap;
    font-family: var(--font-mono);
    font-size: var(--font-size-label);
    letter-spacing: var(--letter-spacing-mono);
    text-transform: uppercase;
    color: var(--color-text-secondary);
    transition: color var(--transition-default);
}

.login-card__divider-link:hover {
    color: var(--color-teal-light);
}

@media (max-width: 480px) {
    .login-card__header {
        padding: var(--space-4) var(--space-5);
    }

    .login-card__body {
        gap: var(--space-4);
        padding: var(--space-5);
    }
}

</style>
