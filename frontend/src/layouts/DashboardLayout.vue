<template>
  <div class="flex h-screen" style="background:#F5F6FA">

    <!-- Sidebar -->
    <aside class="w-60 flex flex-col bg-white border-r border-gray-100 shadow-sm">

      <!-- Logo -->
      <div class="px-6 py-5 border-b border-gray-100">
        <div class="text-2xl font-extrabold tracking-tight select-none">
          <span style="color:#0ABFB8">Raku</span><span style="color:#F5A623">sell</span>
        </div>
        <p class="text-xs text-gray-400 mt-0.5 font-medium">AI Sales Assistant</p>
      </div>

      <!-- Nav -->
      <nav class="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          custom
          v-slot="{ isActive, navigate }"
        >
          <button
            @click="navigate"
            class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-150 group"
            :class="isActive
              ? 'text-white shadow-sm'
              : 'text-gray-500 hover:bg-gray-50 hover:text-gray-800'"
            :style="isActive ? 'background:linear-gradient(135deg,#0ABFB8,#08A89F)' : ''"
          >
            <img
              :src="item.gif"
              :alt="item.label"
              class="w-6 h-6 object-contain flex-shrink-0 transition-transform duration-200 group-hover:scale-110"
            />
            <span class="text-sm font-semibold">{{ item.label }}</span>
          </button>
        </router-link>
      </nav>

      <!-- User info + logout -->
      <div class="px-4 py-4 border-t border-gray-100">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold"
               style="background:linear-gradient(135deg,#0ABFB8,#F5A623)">
            {{ auth.user?.username?.[0]?.toUpperCase() || 'A' }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold text-gray-800 truncate">{{ auth.user?.username || 'Admin' }}</p>
            <p class="text-xs font-medium"
               :style="auth.isAdmin ? 'color:#0ABFB8' : 'color:#F5A623'">
              {{ auth.isAdmin ? 'Admin' : 'Manager' }}
            </p>
          </div>
        </div>
        <button
          @click="logout"
          class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h6a2 2 0 012 2v1"/>
          </svg>
          Выйти
        </button>
      </div>
    </aside>

    <!-- Main -->
    <main class="flex-1 overflow-auto">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

import chatsGif     from '@/assets/chats.gif'
import clientsGif   from '@/assets/customers.gif'
import promptsGif   from '@/assets/prompts.gif'
import knowledgeGif from '@/assets/knowledge base.gif'
import logsGif      from '@/assets/logs.gif'
import statusGif    from '@/assets/status.gif'

const auth = useAuthStore()
const router = useRouter()

const allNavItems = [
  { path: '/chats',     gif: chatsGif,     label: 'Чаты' },
  { path: '/clients',   gif: clientsGif,   label: 'Клиенты' },
  { path: '/prompts',   gif: promptsGif,   label: 'Промпты' },
  { path: '/knowledge', gif: knowledgeGif, label: 'База знаний' },
  { path: '/logs',      gif: logsGif,      label: 'Логи' },
  { path: '/status',    gif: statusGif,    label: 'Статус' },
  { path: '/users',     gif: clientsGif,   label: 'Пользователи', adminOnly: true },
]

const navItems = computed(() =>
  allNavItems.filter(item => !item.adminOnly || auth.isAdmin)
)

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
