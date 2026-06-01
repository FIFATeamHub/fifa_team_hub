import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import router from '../router/index'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))

  const isAuthenticated = computed(() => !!token.value)

  const apiUrl = import.meta.env.VITE_API_URL

  async function login(credenciais) {
    const resposta = await fetch(`${apiUrl}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(credenciais)
    })

    if (resposta.status === 401) {
      throw { status: 401 }
    }

    if (!resposta.ok) {
      throw new Error(`Falha no login: ${resposta.status}`)
    }

    const data = await resposta.json()

    // const resposta = await api.post('/auth/login', { email, password }) # IMPLEMENTAR COM AXIOS
    // const dados = resposta.data

    token.value = data.token
    localStorage.setItem('token', data.token)

    await fetchMe()

    router.push("/dashboard")
  }

  const logout = () => {
 
  user.value = null

  token.value = null
 
  localStorage.removeItem('token')
}

  async function fetchMe() {
    const res = await fetch(`${apiUrl}/auth/me`, {
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    })

    if (!res.ok) {
      throw new Error(`Falha ao buscar usuario: ${res.status}`)
    }

    const data = await res.json()
    user.value = data || null
    return user.value
  }

  return { user, token, isAuthenticated, login, logout, fetchMe }

})