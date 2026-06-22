import { createRouter, createWebHistory } from 'vue-router'
import homeView from '../views/homeView.vue'
import teamView from '../views/teamView.vue'
import loginView from '../views/loginView.vue'
import registerView from '../views/registerView.vue'
import dashboardView from '../views/dashboardView.vue'
import uploadView from '../views/uploadView.vue'
import auditView from '../views/auditView.vue'
import noAcessView from '../views/403View.vue'
import { useAuthStore } from '../stores/auth'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
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
      component: loginView
    },
    {
      path: '/cadastro',
      name: 'cadastro',
      component: registerView
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      meta: {requiresAuth: true},
      component: dashboardView
    },
    {
      path: '/upload',
      name: 'upload',
      meta: {requiresAuth: true},
      component: uploadView
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

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: 'login' }
  }

  if (to.meta.requiresAuth && authStore.isAuthenticated && !authStore.user) {
    try {
      await authStore.fetchMe()
    } catch (error) {
      authStore.logout()
      return { name: 'login' }
    }
  }

  if (to.name == 'audit'){
    // Bloqueio temporariamente removido para teste de tela
    return true
  }

  return true

})

export default router