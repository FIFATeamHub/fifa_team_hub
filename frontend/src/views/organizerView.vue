<!-- frontend/src/views/organizerView.vue -->
<template>
  <div class="organizer-view">

    <section class="organizer-hero">
      <div class="organizer-hero__bg"></div>
      <div class="organizer-hero__overlay"></div>
      <div class="organizer-hero__edge"></div>
      <h1 class="organizer-hero__title">Criar Seleção</h1>
      <p class="organizer-hero__subtitle">Cadastre uma nova Seleção e o Auditor responsável por ela</p>
    </section>

    <div class="organizer-body">
      <div class="organizer-card">

        <form class="organizer-form" @submit.prevent="handleSubmit">

          <fieldset class="organizer-form__fieldset">
            <legend class="organizer-form__legend">Dados da Seleção</legend>

            <div class="form-field">
              <label for="selectionName" class="form-field__label">Nome da Seleção</label>
              <input
                id="selectionName"
                v-model="form.name"
                type="text"
                required
                class="form-field__input"
                placeholder="Ex: Brasil"
              >
            </div>

            <div class="form-field">
              <label for="selectionCode" class="form-field__label">Código da Seleção</label>
              <input
                id="selectionCode"
                v-model="form.code"
                type="text"
                required
                maxlength="3"
                minlength="3"
                class="form-field__input"
                placeholder="Ex: BRA"
              >
              <span class="form-field__hint">Exatamente 3 letras, deve ser único</span>
            </div>
          </fieldset>

          <fieldset class="organizer-form__fieldset">
            <legend class="organizer-form__legend">Dados do Auditor</legend>

            <div class="form-field">
              <label for="auditorName" class="form-field__label">Nome do Auditor</label>
              <input
                id="auditorName"
                v-model="form.auditor_name"
                type="text"
                required
                class="form-field__input"
                placeholder="Nome completo do auditor"
              >
            </div>

            <div class="form-field">
              <label for="auditorEmail" class="form-field__label">Email do Auditor</label>
              <input
                id="auditorEmail"
                v-model="form.auditor_email"
                type="email"
                required
                class="form-field__input"
                placeholder="auditor@email.com"
              >
            </div>

            <div class="form-field">
              <label for="auditorPassword" class="form-field__label">Senha do Auditor</label>
              <input
                id="auditorPassword"
                v-model="form.auditor_password"
                type="password"
                required
                minlength="8"
                class="form-field__input"
              >
              <span class="form-field__hint">Mínimo de 8 caracteres</span>
            </div>
          </fieldset>

          <p v-if="errorMessage" class="organizer-form__error">{{ errorMessage }}</p>
          <p v-if="successMessage" class="organizer-form__success">{{ successMessage }}</p>

          <button type="submit" class="organizer-form__submit" :disabled="submitting">
            {{ submitting ? 'Criando...' : 'Criar Seleção' }}
          </button>
        </form>
      </div>

      <section class="organizer-list">
        <h2 class="organizer-list__title">Seleções cadastradas</h2>
        <ul class="organizer-list__items">
          <li v-for="item in selections" :key="item.id" class="organizer-list__item">
            <span class="organizer-list__code">{{ item.code }}</span>
            <span class="organizer-list__name">{{ item.name }}</span>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">

import { onMounted, reactive, ref } from 'vue'
import api from '@/services/api'

interface SelectionSummary {
  id: string
  name: string
  code: string
}

const selections = ref<SelectionSummary[]>([])

const form = reactive({
  name: '',
  code: '',
  auditor_name: '',
  auditor_email: '',
  auditor_password: '',
})

const submitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const fetchSelections = async () => {
  try {
    const response = await api.get('/api/selection/')
    selections.value = response.data
  } catch (err) {
    console.error('Selections Fetch Error:', err)
  }
}

const resetForm = () => {
  form.name = ''
  form.code = ''
  form.auditor_name = ''
  form.auditor_email = ''
  form.auditor_password = ''
}

const handleSubmit = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  submitting.value = true

  try {
    await api.post('/api/selection/', { ...form })

    successMessage.value = 'Seleção e Auditor criados com sucesso!'
    resetForm()
    await fetchSelections()
  } catch (err) {
    const erro = err as { response?: { data?: { error?: string } } }
    errorMessage.value = erro.response?.data?.error || 'Erro ao criar a Seleção.'
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchSelections()
})

</script>

<style scoped>

.organizer-view {
  background-color: var(--color-bg-base);
  min-height: 100vh;
}

.organizer-hero {
  position: relative;
  overflow: hidden;
  padding: calc(var(--space-16) * 1.2) var(--padding-page-x);
  background-color: var(--color-bg-base);
}

.organizer-hero__bg {
  position: absolute;
  inset: 0;
  background-image: url('/img/audit-hero-2.png');
  background-size: cover;
  background-position: center;
  z-index: 0;
}

.organizer-hero__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg,
    color-mix(in srgb, var(--color-bg-base) 85%, transparent) 0%,
    color-mix(in srgb, var(--color-bg-base) 60%, transparent) 55%,
    color-mix(in srgb, var(--color-bg-mid) 35%, transparent) 100%);
  z-index: 1;
}

.organizer-hero__edge {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  height: 1px;
  background: linear-gradient(90deg,
    color-mix(in srgb, var(--color-gold) 50%, transparent),
    color-mix(in srgb, var(--color-gold) 20%, transparent),
    transparent);
  z-index: 2;
}

.organizer-hero__title {
  position: relative;
  z-index: 3;
  font-family: var(--font-heading);
  font-weight: var(--font-weight-black);
  font-size: var(--font-size-display);
  letter-spacing: var(--letter-spacing-tight);
  line-height: var(--line-height-display);
  color: var(--color-text-primary);
}

.organizer-hero__subtitle {
  position: relative;
  z-index: 3;
  margin-top: var(--space-2);
  color: var(--color-text-secondary);
}

.organizer-body {
  display: grid;
  grid-template-columns: minmax(0, 480px) 1fr;
  gap: var(--space-8);
  padding: var(--space-10) var(--padding-page-x);
}

.organizer-card {
  background-color: #101827;
  border: 1px solid rgba(154, 168, 186, 0.15);
  border-radius: 12px;
  padding: var(--space-8);
}

.organizer-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.organizer-form__fieldset {
  border: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.organizer-form__legend {
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 13px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #D4AF37;
  padding-bottom: var(--space-2);
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field__label {
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  color: #9AA8BA;
}

.form-field__input {
  background-color: #07001D;
  border: 1px solid rgba(154, 168, 186, 0.15);
  padding: 12px;
  border-radius: 6px;
  color: #F4F7FB;
  font-family: 'Inter', sans-serif;
}

.form-field__input:focus {
  outline: none;
  border-color: #0F766E;
  box-shadow: 0 0 10px rgba(15, 118, 110, 0.3);
}

.form-field__hint {
  font-size: 12px;
  color: #9AA8BA;
}

.organizer-form__error {
  margin: 0;
  padding: 12px 16px;
  background-color: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 6px;
  color: #EF4444;
  font-family: 'Inter', sans-serif;
  font-size: 13px;
}

.organizer-form__success {
  margin: 0;
  padding: 12px 16px;
  background-color: rgba(15, 118, 110, 0.15);
  border: 1px solid rgba(15, 118, 110, 0.3);
  border-radius: 6px;
  color: #0F766E;
  font-family: 'Inter', sans-serif;
  font-size: 13px;
}

.organizer-form__submit {
  background-color: #D4AF37;
  border: none;
  border-radius: 6px;
  padding: 14px;
  color: #07001D;
  font-family: 'Inter', sans-serif;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.2s;
}

.organizer-form__submit:hover {
  opacity: 0.85;
}

.organizer-form__submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.organizer-list {
  background-color: #101827;
  border: 1px solid rgba(154, 168, 186, 0.15);
  border-radius: 12px;
  padding: var(--space-8);
  height: fit-content;
}

.organizer-list__title {
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 16px;
  color: #F4F7FB;
  margin: 0 0 var(--space-4) 0;
}

.organizer-list__items {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.organizer-list__item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 6px;
  background-color: #1D2333;
}

.organizer-list__code {
  font-family: 'JetBrains Mono', monospace;
  color: #D4AF37;
  font-size: 12px;
  font-weight: bold;
}

.organizer-list__name {
  font-family: 'Inter', sans-serif;
  color: #F4F7FB;
  font-size: 14px;
}

@media (max-width: 900px) {
  .organizer-body {
    grid-template-columns: 1fr;
  }
}

</style>
