import { ref, reactive, watch } from 'vue'
import api from '@/services/api'

export type LogAction = 'LOGIN' | 'LOGOUT' | 'DELETE' | 'UPLOAD' | 'DOWNLOAD' | 'ACCESS_DENIED'

export interface AuditLog {
  id: string
  user_id: string
  action: LogAction
  resource_id: string | null
  status: 'SUCCESS' | 'FAILED' | 'WARNING'
  ip_address: string
  details: Record<string, unknown> | string
  created_at: string
}

interface Pagination {
  page: number
  per_page: number
  total: number
  pages: number
}

export function useAuditLogs() {

  const logs = ref<AuditLog[]>([])
  const loading = ref(false)
  const error = ref('')

  const filters = reactive({
    page: 1,
    action: '',
    startDate: '',
    endDate: ''
  })

  const pagination = ref<Pagination>({
    page: 1,
    per_page: 20,
    total: 0,
    pages: 1
  })

  const fetchAuditLogs = async () => {
    loading.value = true
    error.value = ''
    try {
      const response = await api.get('/api/audit/', {
        params: {
          page: filters.page,
          action: filters.action || undefined,
          start_date: filters.startDate || undefined,
          end_date: filters.endDate || undefined
        }
      })

      logs.value = response.data.data
      pagination.value = response.data.pagination
    } catch (err) {
      console.error('Audit Log Fetch Error:', err)
      error.value = 'Erro ao buscar logs de auditoria.'
    } finally {
      loading.value = false
    }
  }

  // Escuta alterações nos filtros para resetar a página e buscar novamente
  watch(() => [filters.action, filters.startDate, filters.endDate], () => {
    filters.page = 1
    fetchAuditLogs()
  })

  // Escuta alteração de página
  watch(() => filters.page, () => {
    fetchAuditLogs()
  })

  return {
    logs,
    loading,
    error,
    filters,
    pagination,
    fetchAuditLogs
  }

}
