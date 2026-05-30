import { createRouter, createWebHistory } from 'vue-router'
import homeView from '../views/homeView.vue'
import teamView from '../views/teamView.vue'

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
    }
  ]
})

export default router