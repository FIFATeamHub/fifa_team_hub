import { ref, reactive, watch } from 'vue'


interface AuditLog {
  id: string
  user: string
  action: string
  status: 'SUCCESS' | 'FAILED' | 'WARNING'
  ip_address: string
  timestamp: string
  details: Record<string, any> | string
}


export function useAuditLogs() {
    
    const logs = ref<AuditLog[]>([])
    const loading = ref(false)
    const totalPages = ref(1)

    const filters = reactive({
    page: 1,
    action: '',
    startDate: '',
    endDate: ''
    })

}