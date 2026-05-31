import { createRouter, createWebHistory } from 'vue-router'
import homeView from '../views/homeView.vue'
import teamView from '../views/teamView.vue'
import loginView from '../views/loginView.vue'
import dashboardView from '../views/dashboardView.vue'
import uploadView from '../views/uploadView.vue'
import auditView from '../views/auditView.vue'
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
    }
  ]
})

router.beforeEach((to,from,next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({name: 'login'})
  } else{
    next()
  }
})

export default router