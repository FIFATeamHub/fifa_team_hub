<template>
  <section class="dash-hero">
    <div class="dash-hero__media" aria-hidden="true"></div>
    <div class="dash-hero__content">
      <h1 class="dash-hero__title">
        <span class="dash-hero__title-muted">Seja bem-vindo,</span>
        <span class="dash-hero__title-strong">{{ firstName }}.</span>
      </h1>
    </div>
  </section>

  <div class="conteudo-container">

    <main class="conteudo-principal">

      <section class="dash-section">
        <div class="dash-section__head">
          <h2 class="dash-section__title">Ações rápidas</h2>
          <span class="dash-section__hint">Atalhos liberados para o seu perfil.</span>
        </div>

        <div class="quick-actions-grid">

          <QuickActionCard
            v-if="can('upload:documents')"
            title="Upload"
            subtitle="Enviar arquivos"
            @activate="isModalOpen = true"
          >
            <template #icon>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 15V4m0 0-4 4m4-4 4 4" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M4 15v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </template>
          </QuickActionCard>

          <QuickActionCard
            title="Listar Documentos"
            subtitle="Ver todos os arquivos"
            to="/documentos"
          >
            <template #icon>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 6h9l2 3h5v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1Z" />
              </svg>
            </template>
          </QuickActionCard>

        </div>
      </section>

      <section class="dash-section">
        <div class="dash-section__head">
          <div class="dash-section__heading">
            <span class="dash-section__eyebrow">Dossiê Operacional</span>
            <h2 class="dash-section__title">Documentos recentes</h2>
          </div>
        </div>

        <DocumentsList ref="documentsListRef" />
      </section>

      <section v-if="authStore.user?.role === 'ATHELETE'" class="dash-section">
        <div class="dash-section__head">
          <div class="dash-section__heading">
            <span class="dash-section__eyebrow">Sala de Controle</span>
            <h2 class="dash-section__title">Pendências críticas</h2>
          </div>
        </div>

        <div v-if="pendingLoading" class="dash-state">
          <div class="dash-spinner"></div>
          <p>Carregando pendências...</p>
        </div>

        <div v-else-if="pendingDocuments.length > 0" class="feed-card">
          <div
            v-for="doc in pendingDocuments"
            :key="doc.doc_type"
            class="feed-row feed-row--warning"
          >
            <svg class="feed-row__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 9v4m0 4h.01M10.3 3.9 2.6 17a1.5 1.5 0 0 0 1.3 2.2h16.2a1.5 1.5 0 0 0 1.3-2.2L13.7 3.9a1.5 1.5 0 0 0-2.6 0Z" />
            </svg>
            <span class="feed-row__text">Envie seu documento: {{ formatDocType(doc.doc_type) }}</span>
          </div>
        </div>

        <p v-else class="dash-empty">Nenhuma pendência no momento.</p>
      </section>

      <section
        v-if="authStore.user?.role === 'AUDITOR'"
        class="dash-section"
      >
        <div class="dash-section__head">
          <div class="dash-section__heading">
            <span class="dash-section__eyebrow">Caixa-Preta</span>
            <h2 class="dash-section__title">Atividade recente</h2>
          </div>
        </div>

        <div v-if="auditLoading" class="dash-state">
          <div class="dash-spinner"></div>
          <p>Carregando atividade...</p>
        </div>

        <div v-else-if="auditLogs.length > 0" class="feed-card">
          <div v-for="log in auditLogs.slice(0, 5)" :key="log.id" class="feed-row">
            <span class="feed-row__dot" aria-hidden="true"></span>
            <div class="feed-row__body">
              <span class="feed-row__title">{{ actionLabel(log.action) }}</span>
              <span class="feed-row__time">{{ formatDate(log.created_at) }}</span>
            </div>
          </div>
        </div>

        <p v-else class="dash-empty">Nenhuma atividade recente.</p>
      </section>

    </main>

    <footer class="dash-footer">
      <span class="dash-footer__version">FIFA Team Hub &bull; v1.0.0</span>
      <button @click="efetuarLogout" class="botao-sair">Sair do Sistema</button>
    </footer>

  </div>

  <UploadDocumentModal
    :isOpen="isModalOpen"
    :onClose="() => isModalOpen = false"
    :onSuccess="aoReceberDocumento"
  />
</template>


<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useRouter } from 'vue-router'
import UploadDocumentModal from '@/components/documents/UploadDocumentModal.vue'
import { usePermissions } from '@/composables/usePermissions'
import DocumentsList from '@/components/documents/DocumentsList.vue'
import QuickActionCard from '@/components/dashboard/QuickActionCard.vue'
import { useDocuments } from '@/composables/useDocuments'
import { useAuditLogs, type LogAction } from '@/composables/useAuditLogs'

const authStore = useAuthStore()
const router    = useRouter()
const { can }   = usePermissions()

const isModalOpen = ref(false)
const documentsListRef = ref<InstanceType<typeof DocumentsList> | null>(null)

const firstName = computed(() => {
  const name = authStore.user?.full_name
  if (!name) return 'Usuário'
  return name.trim().split(/\s+/)[0]
})

const efetuarLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

// Chamada pelo modal ao completar upload com sucesso: atualiza a lista visível
function aoReceberDocumento() {
  documentsListRef.value?.refresh()
}

// --- Pendências críticas (ATHELETE) ---
const { pendingDocuments, loading: pendingLoading, fetchPendingDocuments } = useDocuments()

const docTypeLabels: Record<string, string> = {
  PASSPORT: 'Passaporte',
  CONVOCADO: 'Convocação',
  LAUDO_MEDICO: 'Laudo Médico',
  RELATORIO_TATICO: 'Relatório Tático',
  ESQUEMA_JOGADAS: 'Esquema de Jogadas'
}

function formatDocType(type: string) {
  return docTypeLabels[type] ?? type
}

// --- Atividade recente (AUDITOR) ---
const { logs: auditLogs, loading: auditLoading, fetchAuditLogs } = useAuditLogs()

const actionLabels: Record<LogAction, string> = {
  LOGIN: 'Login realizado',
  LOGOUT: 'Logout realizado',
  DELETE: 'Documento excluído',
  UPLOAD: 'Documento enviado',
  DOWNLOAD: 'Documento baixado',
  ACCESS_DENIED: 'Acesso negado'
}

function actionLabel(action: LogAction) {
  return actionLabels[action] ?? action
}

function formatDate(date: string) {
  return new Date(date).toLocaleString('pt-BR')
}

onMounted(() => {
  if (authStore.user?.role === 'ATHELETE') {
    fetchPendingDocuments()
  }
  if (authStore.user?.role === 'AUDITOR') {
    fetchAuditLogs()
  }
})
</script>

<style scoped>

.conteudo-container {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: var(--padding-section) var(--padding-page-x);
  display: flex;
  flex-direction: column;
  gap: var(--space-14);
}

.dash-hero {
  position: relative;
  width: 100%;
  min-height: 22rem;
  background-color: var(--color-bg-deep);
  border-bottom: 1px solid var(--color-border-default);
  overflow: hidden;
}

.dash-hero__media {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(180deg, rgba(4, 12, 24, 0.15) 0%, rgba(4, 12, 24, 0.92) 100%),
    linear-gradient(100deg, var(--color-bg-deep) 0%, rgba(4, 12, 24, 0.55) 40%, rgba(4, 12, 24, 0.05) 75%),
    url('@/img/Gemini_Generated_Image_5y62735y62735y62.png');
  background-size: cover;
  background-position: center;
}

.dash-hero__content {
  position: relative;
  z-index: 1;
  max-width: var(--max-width);
  min-height: 22rem;
  margin: 0 auto;
  padding: var(--padding-section) var(--padding-page-x);
  display: flex;
  align-items: flex-end;
}

.dash-hero__title {
  font-family: var(--font-heading);
  font-weight: var(--font-weight-black);
  font-size: var(--font-size-display);
  line-height: var(--line-height-display);
  letter-spacing: var(--letter-spacing-tight);
}

.dash-hero__title-muted {
  display: block;
  color: var(--color-text-tertiary);
}

.dash-hero__title-strong {
  display: block;
  color: var(--color-text-primary);
}

.conteudo-principal {
  display: flex;
  flex-direction: column;
  gap: var(--space-14);
}

.dash-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.dash-section__head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--space-3);
}

.dash-section__heading {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.dash-section__eyebrow {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-family: var(--font-mono);
  font-size: var(--font-size-label);
  letter-spacing: var(--letter-spacing-label);
  text-transform: uppercase;
  color: var(--color-gold);
}

.dash-section__eyebrow::before {
  content: '';
  width: var(--space-6);
  height: 1px;
  background-color: var(--color-gold);
}

.dash-section__title {
  font-family: var(--font-heading);
  font-weight: var(--font-weight-black);
  font-size: var(--font-size-h2);
  letter-spacing: var(--letter-spacing-heading);
  color: var(--color-text-primary);
}

.dash-section__hint {
  font-family: var(--font-body);
  font-size: var(--font-size-small);
  color: var(--color-text-tertiary);
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(18rem, 1fr));
  gap: var(--space-6);
}

.dash-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-12);
  color: var(--color-text-secondary);
  font-family: var(--font-body);
  font-size: var(--font-size-body);
}

.dash-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-border-default);
  border-top-color: var(--color-gold);
  border-radius: var(--radius-full);
  animation: dash-spin 1s linear infinite;
}

@keyframes dash-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.dash-empty {
  padding: var(--space-8);
  text-align: center;
  color: var(--color-text-tertiary);
  font-family: var(--font-mono);
  font-size: var(--font-size-label);
  letter-spacing: var(--letter-spacing-mono);
  text-transform: uppercase;
  background-color: var(--color-surface-primary);
  border: 1px solid var(--color-border-default);
  border-radius: var(--radius-lg);
}

.feed-card {
  display: flex;
  flex-direction: column;
  padding: var(--space-3) var(--padding-card);
  background-color: var(--color-surface-primary);
  border: 1px solid var(--color-border-default);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-card);
}

.feed-row {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) 0;
}

.feed-row + .feed-row {
  border-top: 1px solid var(--color-border-subtle);
}

.feed-row--warning {
  color: var(--color-text-secondary);
}

.feed-row__icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  color: var(--color-text-tertiary);
}

.feed-row__text {
  font-family: var(--font-body);
  font-size: var(--font-size-body);
  color: var(--color-text-secondary);
}

.feed-row__dot {
  flex-shrink: 0;
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  background-color: var(--color-gold);
}

.feed-row__body {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  flex: 1;
  gap: var(--space-4);
}

.feed-row__title {
  font-family: var(--font-body);
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-body);
  color: var(--color-text-primary);
}

.feed-row__time {
  font-family: var(--font-mono);
  font-size: var(--font-size-label);
  letter-spacing: var(--letter-spacing-label);
  color: var(--color-text-tertiary);
  white-space: nowrap;
}

.dash-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding-top: var(--space-8);
  border-top: 1px solid var(--color-border-subtle);
}

.dash-footer__version {
  font-family: var(--font-mono);
  font-size: var(--font-size-label);
  letter-spacing: var(--letter-spacing-label);
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.botao-sair {
  padding: var(--space-3) var(--space-6);
  border: 1px solid var(--color-danger-border);
  border-radius: var(--radius-sm);
  color: var(--color-danger);
  font-family: var(--font-body);
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-small);
  transition: background-color var(--transition-default), color var(--transition-default);
}

.botao-sair:hover {
  background-color: var(--color-danger-bg);
}

@media (max-width: 480px) {
  .quick-actions-grid {
    grid-template-columns: 1fr;
  }

  .dash-footer {
    flex-direction: column;
    align-items: flex-start;
  }
}

</style>