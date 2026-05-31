import { defineStore } from 'pinia'
import {ref, computed} from 'vue'

export const useAuthStore = defineStore('auth', () => {
    const user = ref(null)
    const token = ref(null)


const isAuthenticated = computed(() => !!token.value)

async function login() {}

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