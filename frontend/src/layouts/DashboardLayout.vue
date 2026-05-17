<template>
  <div class="flex h-screen" style="background:#F0F2F8">

    <!-- Sidebar -->
    <aside class="w-64 flex flex-col bg-white border-r border-gray-100" style="box-shadow: 2px 0 12px rgba(0,0,0,0.06)">

      <!-- Logo -->
      <div class="px-6 py-6 border-b border-gray-100">
        <div class="text-2xl font-extrabold tracking-tight select-none">
          <span style="color:#0ABFB8">Raku</span><span style="color:#F5A623">sell</span>
        </div>
        <p class="text-xs text-gray-400 mt-1 font-medium tracking-wide uppercase">AI Sales Assistant</p>
      </div>

      <!-- Nav -->
      <nav class="flex-1 px-3 py-5 space-y-1 overflow-y-auto">
        <p class="text-xs font-semibold text-gray-400 uppercase tracking-widest px-3 mb-3">Меню</p>
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          custom
          v-slot="{ isActive, navigate }"
        >
          <button
            @click="navigate"
            class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group"
            :class="isActive ? 'text-white shadow-md' : 'text-gray-500 hover:bg-gray-50 hover:text-gray-800'"
            :style="isActive ? 'background: linear-gradient(135deg, #0ABFB8, #08A89F)' : ''"
          >
            <span class="w-8 h-8 flex items-center justify-center rounded-lg flex-shrink-0 transition-all duration-200"
              :style="isActive ? 'background:rgba(255,255,255,0.2)' : 'background:#F5F6FA'"
            >
              <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                :class="isActive ? 'text-white' : 'text-gray-500 group-hover:text-gray-700'"
                style="width:18px;height:18px"
                stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                v-html="item.icon"
              />
            </span>
            <span class="text-sm font-semibold">{{ item.label }}</span>
            <span v-if="item.badge" class="ml-auto text-xs font-bold bg-white/30 text-white rounded-full px-1.5 py-0.5">
              {{ item.badge }}
            </span>
          </button>
        </router-link>
      </nav>

      <!-- User info + logout -->
      <div class="px-4 py-4 border-t border-gray-100 bg-gray-50/60">
        <div class="flex items-center gap-3 mb-3 px-1">
          <div class="w-9 h-9 rounded-xl flex items-center justify-center text-white text-sm font-bold flex-shrink-0"
               style="background:linear-gradient(135deg,#0ABFB8,#08A89F)">
            {{ auth.user?.username?.[0]?.toUpperCase() || 'A' }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-bold text-gray-800 truncate">{{ auth.user?.username || 'Admin' }}</p>
            <p class="text-xs font-semibold"
               :style="auth.isAdmin ? 'color:#0ABFB8' : 'color:#F5A623'">
              {{ auth.isAdmin ? 'Admin' : 'Manager' }}
            </p>
          </div>
        </div>
        <button
          @click="logout"
          class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-400 hover:text-red-500 hover:bg-red-50 transition-all duration-200"
        >
          <svg style="width:16px;height:16px" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9"/>
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

const auth = useAuthStore()
const router = useRouter()

const allNavItems = [
  {
    path: '/app/chats',
    label: 'Чаты',
    icon: '<path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>',
  },
  {
    path: '/app/clients',
    label: 'Клиенты',
    icon: '<path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/>',
  },
  {
    path: '/app/prompts',
    label: 'Промпты',
    icon: '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>',
  },
  {
    path: '/app/knowledge',
    label: 'База знаний',
    icon: '<path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/>',
  },
  {
    path: '/app/logs',
    label: 'Логи',
    icon: '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>',
  },
  {
    path: '/app/status',
    label: 'Статус',
    icon: '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
  },
  {
    path: '/app/users',
    label: 'Пользователи',
    icon: '<path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    adminOnly: true,
  },
]

const navItems = computed(() =>
  allNavItems.filter(item => !item.adminOnly || auth.isAdmin)
)

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
