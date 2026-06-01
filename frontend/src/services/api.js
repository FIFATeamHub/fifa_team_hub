import axios from 'axios'
import router from '../router' // Importa o roteador para redirecionar se der erro 401

const api = axios.create({
  // Pega automaticamente a URL que você configurou no arquivo .env
  baseURL: import.meta.env.VITE_API_URL 
})

// 1. Interceptor de Requisição (Injeta o Token)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token') // Busca o token salvo no navegador
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, (error) => {
  return Promise.reject(error)
})

// 2. Interceptor de Resposta (Pega erro 401)
api.interceptors.response.use(
  (response) => response
  (error) => {
    // Se o backend responder 401, limpa os dados salvos e manda pro Login
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default api