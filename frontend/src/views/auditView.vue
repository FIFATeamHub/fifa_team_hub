<!-- frontend/src/views/auditView.vue -->
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useAuditLogs, type AuditLog } from '@/composables/useAuditLogs'
import { ShieldCheck, ShieldAlert, Search, Calendar, Eye } from 'lucide-vue-next'

const { logs, loading, error, filters, pagination, fetchAuditLogs } = useAuditLogs()

// Estado para o modal de detalhes de segurança
const selectedDetails = ref<string | null>(null)
const isModalOpen = ref(false)

const openDetailsModal = (details: AuditLog['details']) => {
  if (typeof details === 'string') {
    selectedDetails.value = details
    isModalOpen.value = true
    return
  }

  // Tratamento preventivo de segurança (Double-Guard Sanitization)
  const sanitized: Record<string, unknown> = { ...details }
  if (sanitized.password) sanitized.password = '********'
  if (sanitized.token) sanitized.token = '********'

  selectedDetails.value = JSON.stringify(sanitized, null, 2)
  isModalOpen.value = true
}

const formatDate = (date: string) => {
  return date ? new Date(date).toLocaleString('pt-BR') : '—'
}

onMounted(() => {
  fetchAuditLogs()
})
</script>

<template>
  <div class="audit-container">
    <!-- Header da Tela -->
    <header class="audit-header">
      <div class="title-block">
        <span class="system-badge">[ AMBIENTE VERIFICADO ]</span>
        <h1>Terminal de Integridade e Auditoria</h1>
      </div>
    </header>

    <!-- Barra de Filtros Avançados -->
    <section class="filter-bar">
      <div class="input-group">
        <label><Search :size="14" /> Filtrar por Ação</label>
        <select v-model="filters.action" class="custom-select">
          <option value="">Todas as ações operacionais</option>
          <option value="LOGIN">LOGIN</option>
          <option value="LOGOUT">LOGOUT</option>
          <option value="DELETE">DELETE</option>
          <option value="UPLOAD">UPLOAD</option>
          <option value="DOWNLOAD">DOWNLOAD</option>
          <option value="ACCESS_DENIED">ACCESS_DENIED</option>
        </select>
      </div>

      <div class="input-group">
        <label><Calendar :size="14" /> Período Inicial</label>
        <input type="date" v-model="filters.startDate" class="custom-input" />
      </div>

      <div class="input-group">
        <label><Calendar :size="14" /> Período Final</label>
        <input type="date" v-model="filters.endDate" class="custom-input" />
      </div>
    </section>

    <!-- Tabela de Dados (Estilo Terminal Corporativo) -->
    <section class="table-container">
      <table class="audit-table">
        <thead>
          <tr>
            <th>Usuário</th>
            <th>Ação</th>
            <th>Status</th>
            <th>Endereço IP</th>
            <th>Timestamp</th>
            <th class="text-center">Dossiê</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading" class="state-row">
            <td colspan="6" class="text-center text-muted">Sincronizando registros com o banco de dados institucional...</td>
          </tr>
          <tr v-else-if="error" class="state-row">
            <td colspan="6" class="text-center text-muted">{{ error }}</td>
          </tr>
          <tr v-else-if="logs.length === 0" class="state-row">
            <td colspan="6" class="text-center text-muted">Nenhum log de auditoria encontrado para os filtros selecionados.</td>
          </tr>
          <tr v-for="log in logs" :key="log.id" v-else>
            <td class="font-ui font-medium text-white">{{ log.user_id }}</td>
            <td><span class="action-badge">{{ log.action }}</span></td>
            <td>
              <span :class="['status-indicator', log.status.toLowerCase()]">
                <ShieldCheck v-if="log.status === 'SUCCESS'" :size="14" />
                <ShieldAlert v-else :size="14" />
                {{ log.status }}
              </span>
            </td>
            <td class="font-mono text-muted">{{ log.ip_address }}</td>
            <td class="font-mono text-muted">{{ formatDate(log.created_at) }}</td>
            <td class="text-center">
              <button @click="openDetailsModal(log.details)" class="btn-inspect" title="Inspecionar Metadados">
                <Eye :size="16" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Paginação Integrada -->
      <div class="pagination-bar" v-if="pagination.pages > 1">
        <button
          :disabled="filters.page === 1"
          @click="filters.page--"
          class="btn-pager"
        >
          &larr; Anterior
        </button>
        <span class="page-indicator">Página {{ pagination.page }} de {{ pagination.pages }}</span>
        <button
          :disabled="filters.page === pagination.pages"
          @click="filters.page++"
          class="btn-pager"
        >
          Próxima &rarr;
        </button>
      </div>
    </section>

    <!-- Modal de Inspeção Crítica de Detalhes -->
    <div v-if="isModalOpen" class="modal-overlay" @click.self="isModalOpen = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3>Metadados do Registro Obscuro</h3>
          <button @click="isModalOpen = false" class="close-button">&times;</button>
        </div>
        <pre class="json-viewer"><code>{{ selectedDetails }}</code></pre>
      </div>
    </div>
  </div>
</template>

<style scoped>
.audit-container {
  padding: 40px;
  background-color: #08111F; /* Midnight Navy */
  min-height: 100vh;
}

.system-badge {
  font-family: 'JetBrains Mono', monospace;
  color: #0F766E; /* Tactical Teal */
  font-size: 12px;
  letter-spacing: 0.05em;
}

.audit-header h1 {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 32px;
  color: #F4F7FB;
  margin-top: 8px;
}

.filter-bar {
  display: flex;
  gap: 24px;
  background-color: #101827; /* Surface Navy */
  padding: 24px;
  border-radius: 12px;
  border: 1px solid rgba(154, 168, 186, 0.15);
  margin: 32px 0 24px 0;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.input-group label {
  font-family: 'Inter', sans-serif;
  color: #9AA8BA; /* Muted Blue Gray */
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.custom-select, .custom-input {
  background-color: #07001D; /* Ink Blue */
  border: 1px solid rgba(154, 168, 186, 0.15);
  padding: 12px;
  border-radius: 6px;
  color: #F4F7FB;
  font-family: 'Inter', sans-serif;
}

.custom-select:focus, .custom-input:focus {
  outline: none;
  border-color: #0F766E;
  box-shadow: 0 0 10px rgba(15, 118, 110, 0.3);
}

.table-container {
  background-color: #101827;
  border-radius: 12px;
  border: 1px solid rgba(154, 168, 186, 0.15);
  overflow: hidden;
}

.audit-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.audit-table th {
  background-color: #1D2333; /* Panel Blue */
  padding: 16px 24px;
  color: #9AA8BA;
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  font-weight: 600;
  border-bottom: 1px solid rgba(154, 168, 186, 0.15);
}

.audit-table td {
  padding: 16px 24px;
  border-bottom: 1px solid rgba(154, 168, 186, 0.1);
  color: #F4F7FB;
}

.font-mono { font-family: 'JetBrains Mono', monospace; font-size: 13px; }
.font-ui { font-family: 'Inter', sans-serif; }
.text-muted { color: #9AA8BA !important; }

.action-badge {
  font-family: 'JetBrains Mono', monospace;
  background-color: #1D2333;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: bold;
  padding: 4px 10px;
  border-radius: 9999px;
}

.status-indicator.success { background-color: rgba(15, 118, 110, 0.15); color: #0F766E; }
.status-indicator.failed { background-color: rgba(239, 68, 68, 0.15); color: #EF4444; }
.status-indicator.warning { background-color: rgba(212, 175, 55, 0.15); color: #D4AF37; }

.btn-inspect {
  background: none;
  border: none;
  color: #D4AF37; /* Signal Gold */
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background 0.2s;
}

.btn-inspect:hover { background-color: rgba(212, 175, 55, 0.1); }

.pagination-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background-color: #1D2333;
  border-top: 1px solid rgba(154, 168, 186, 0.15);
}

.btn-pager {
  background-color: #07001D;
  border: 1px solid rgba(154, 168, 186, 0.15);
  color: #F4F7FB;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
}

.btn-pager:disabled { opacity: 0.4; cursor: not-allowed; }

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100vw; height: 100vh;
  background-color: rgba(8, 17, 31, 0.85);
  display: flex; align-items: center; justify-content: center; z-index: 100;
}
.modal-card {
  background-color: #1D2333;
  border: 1px solid rgba(154, 168, 186, 0.2);
  border-radius: 12px; width: 600px; max-height: 80vh; display: flex; flex-direction: column;
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center; padding: 20px 24px;
  border-bottom: 1px solid rgba(154, 168, 186, 0.15);
}
.json-viewer {
  padding: 24px; background-color: #07001D; margin: 0; overflow-y: auto;
  font-family: 'JetBrains Mono', monospace; color: #0F766E; font-size: 13px;
}
.close-button { background: none; border: none; color: #EF4444; font-size: 24px; cursor: pointer; }
</style>