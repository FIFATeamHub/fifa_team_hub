import axios from 'axios'
import router from '../router' 

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL 
})