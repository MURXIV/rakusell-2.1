import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: () => import('@/views/LandingView.vue'),
    meta: { public: true },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/app',
    component: () => import('@/layouts/DashboardLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/app/chats' },
      { path: 'chats', name: 'Chats', component: () => import('@/views/ChatsView.vue') },
      { path: 'chats/:id', name: 'ChatDetail', component: () => import('@/views/ChatDetailView.vue') },
      { path: 'clients', name: 'Clients', component: () => import('@/views/ClientsView.vue') },
      { path: 'clients/:id', name: 'ClientDetail', component: () => import('@/views/ClientDetailView.vue') },
      { path: 'prompts', name: 'Prompts', component: () => import('@/views/PromptsView.vue') },
      { path: 'knowledge', name: 'Knowledge', component: () => import('@/views/KnowledgeView.vue') },
      { path: 'logs', name: 'Logs', component: () => import('@/views/LogsView.vue') },
      { path: 'status', name: 'Status', component: () => import('@/views/StatusView.vue') },
      { path: 'users', name: 'Users', component: () => import('@/views/UsersView.vue'), meta: { adminOnly: true } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) {
    next('/login')
  } else if (to.meta.adminOnly && !auth.isAdmin) {
    next('/app/chats')
  } else {
    next()
  }
})

export default router
