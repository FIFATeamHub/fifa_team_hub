import { ref } from 'vue'
import api from '@/services/api'

export interface PendingRegistration {
  id: string
  full_name: string
  email: string
  selection_id: string | null
  created_at: string | null
}

export function usePendingRegistrations() {

  const registrations = ref<PendingRegistration[]>([])
  const loading = ref(false)
  const error = ref('')

  const fetchPendingRegistrations = async () => {
    loading.value = true
    error.value = ''
    try {
      const response = await api.get('/api/auth/registrations/pending')
      registrations.value = response.data.data
    } catch (err) {
      console.error('Pending Registrations Fetch Error:', err)
      error.value = 'Erro ao buscar solicitações pendentes.'
    } finally {
      loading.value = false
    }
  }

  const approveRegistration = async (userId: string, role: string) => {
    const response = await api.post(`/api/auth/registrations/${userId}/approve`, { role })
    registrations.value = registrations.value.filter((item) => item.id !== userId)
    return response.data
  }

  const rejectRegistration = async (userId: string) => {
    const response = await api.post(`/api/auth/registrations/${userId}/reject`)
    registrations.value = registrations.value.filter((item) => item.id !== userId)
    return response.data
  }

  return {
    registrations,
    loading,
    error,
    fetchPendingRegistrations,
    approveRegistration,
    rejectRegistration
  }

}
