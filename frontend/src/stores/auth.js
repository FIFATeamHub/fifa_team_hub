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

    const data = await resposta.json()
    token.value = data.token
    localStorage.setItem('token', data.token)

    await fetchMe()

    router.push("/dashboard")
  }

  async function logout() {}

  async function fetchMe() {}

  return {
    user,
    token,
    isAuthenticated,
    login,
    logout,
    fetchMe,
  }
})