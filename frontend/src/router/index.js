import { createRouter, createWebHistory } from 'vue-router'
import homeView from '../views/homeView.vue'
import teamView from '../views/teamView.vue'
import loginView from '../views/loginView.vue'
import registerView from '../views/registerView.vue'
import dashboardView from '../views/dashboardView.vue'
import documentsView from '../views/documentsView.vue'
import auditView from '../views/auditView.vue'
import noAcessView from '../views/403View.vue'
import { useAuthStore } from '../stores/auth'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      meta: {requiresAuth: true},
      component: homeView
    },
    {
      path: '/times',
      name: 'times',
      component: teamView
    },
    {
      path: '/login',
      name: 'login',
      meta: {guestOnly: true},
      component: loginView
    },
    {
      path: '/cadastro',
      name: 'cadastro',
      meta: {guestOnly: true},
      component: registerView
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      meta: {requiresAuth: true},
      component: dashboardView
    },
    {
      path: '/documentos',
      name: 'documentos',
      meta: {requiresAuth: true},
      component: documentsView
    },
    {
      path: '/audit',
      name: 'audit',
      meta: {requiresAuth: true},
      component: auditView
    },
    {
      path: '/403error',
      name: '403',
      meta: {requiresAuth: true},
      component: noAcessView
    }
  ]
})



router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  if (authStore.token && !authStore.user) {
    try {
      await authStore.fetchMe()
    } catch (err) {
      if (err?.status === 401) {
        authStore.logout()
      }
    }
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: 'login' }
  }

  if (to.meta.guestOnly && authStore.isAuthenticated) {
    return { name: 'dashboard' }
  }

  if (to.name == 'audit'){
    const userRole = authStore.user?.role

    if(userRole !== "AUDITOR"){
      return {name : "403"}
    }
  }

  return true

})

export default router