import { createRouter, createWebHistory } from 'vue-router'
import homeView from '../views/homeView.vue'
import teamView from '../views/teamView.vue'
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
      component: dashboardViews
    }
  ]
})

router.beforeEach((to,from,next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !useAuthStore.isAuthenticated) {
    next({name: 'login'})
  } else{
    next()
  }
})

export default router