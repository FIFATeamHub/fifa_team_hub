import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import router from '../router/index'
<<<<<<< HEAD
=======


>>>>>>> e6e1e96 (fetch : logica e página de registros / estilizando algumas tela / organizando arquivos em componentes)

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
<<<<<<< HEAD
=======

  const isAuthenticated = computed(() => !!token.value)

  const apiUrl = import.meta.env.VITE_API_URL
>>>>>>> e6e1e96 (fetch : logica e página de registros / estilizando algumas tela / organizando arquivos em componentes)

  const isAuthenticated = computed(() => !!token.value)

<<<<<<< HEAD
  const apiUrl = import.meta.env.VITE_API_URL

  async function login(credenciais) {
    const resposta = await fetch(`${apiUrl}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(credenciais)
    })

=======


  async function login(credenciais) {
    const resposta = await fetch(`${apiUrl}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(credenciais)
    })

>>>>>>> e6e1e96 (fetch : logica e página de registros / estilizando algumas tela / organizando arquivos em componentes)
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

<<<<<<< HEAD
=======


  async function register(dadosCadastro){

    try{

        const resposta = await api.post('/auth/register', {
            nome: dadosCadastro.nome,
            email: dadosCadastro.email,
            password: dadosCadastro.password,
            cargo: dadosCadastro.cargo
        })
        
        return resposta.data  
    }
    catch (erro) {
    
        if (erro.response) {
        throw { 
            status: erro.response.status, 
            message: erro.response.data.message || 'Erro ao realizar cadastro.' 
        }
        }
        throw erro
    }


  }



>>>>>>> e6e1e96 (fetch : logica e página de registros / estilizando algumas tela / organizando arquivos em componentes)
  const logout = () => {
 
  user.value = null

  token.value = null
 
  localStorage.removeItem('token')
}

<<<<<<< HEAD
=======




>>>>>>> e6e1e96 (fetch : logica e página de registros / estilizando algumas tela / organizando arquivos em componentes)
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

<<<<<<< HEAD
  return { user, token, isAuthenticated, login, logout, fetchMe }
=======
  return { user, token, isAuthenticated, login, logout, fetchMe, register }
>>>>>>> e6e1e96 (fetch : logica e página de registros / estilizando algumas tela / organizando arquivos em componentes)

})