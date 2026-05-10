<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-800">Статус системы</h2>
      <div class="flex items-center gap-3">
        <span class="text-xs text-gray-400">Обновлено: {{ lastUpdated }}</span>
        <button @click="refresh" class="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-lg">
          Обновить
        </button>
      </div>
    </div>

    <!-- Health checks -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div
        v-for="(check, name) in health.checks"
        :key="name"
        class="bg-white rounded-xl shadow p-4 flex items-center gap-3"
      >
        <span class="text-2xl">{{ serviceIcon(name) }}</span>
        <div>
          <p class="text-xs text-gray-500 capitalize">{{ serviceName(name) }}</p>
          <div class="flex items-center gap-1.5 mt-0.5">
            <span
              class="inline-block w-2 h-2 rounded-full"
              :class="check.status === 'ok' ? 'bg-green-500' : check.status === 'warning' ? 'bg-yellow-400' : 'bg-red-500'"
            ></span>
            <span class="text-sm font-semibold" :class="check.status === 'ok' ? 'text-green-700' : check.status === 'warning' ? 'text-yellow-600' : 'text-red-600'">
              {{ check.status === 'ok' ? 'OK' : check.status === 'warning' ? 'Внимание' : 'Ошибка' }}
            </span>
            <span v-if="check.workers !== undefined" class="text-xs text-gray-400">({{ check.workers }} воркеров)</span>
          </div>
          <p v-if="check.detail" class="text-xs text-red-400 mt-0.5 truncate max-w-[150px]" :title="check.detail">{{ check.detail }}</p>
        </div>
      </div>

      <!-- Overall status card -->
      <div class="bg-white rounded-xl shadow p-4 flex items-center gap-3">
        <span class="text-2xl">{{ health.status === 'ok' ? '✅' : '⚠️' }}</span>
        <div>
          <p class="text-xs text-gray-500">Система</p>
          <p class="text-sm font-semibold mt-0.5" :class="health.status === 'ok' ? 'text-green-700' : 'text-yellow-600'">
            {{ health.status === 'ok' ? 'Работает' : 'Деградация' }}
          </p>
        </div>
      </div>
    </div>

    <!-- Stats grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
      <!-- Chats -->
      <div class="bg-white rounded-xl shadow p-5">
        <h3 class="text-sm font-semibold text-gray-500 mb-3">Чаты</h3>
        <div class="space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Всего</span>
            <span class="font-bold text-gray-800">{{ stats.chats?.total ?? '—' }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Активных</span>
            <span class="font-semibold text-green-600">{{ stats.chats?.active ?? '—' }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Ожидают</span>
            <span class="font-semibold text-yellow-600">{{ stats.chats?.pending ?? '—' }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Закрытых</span>
            <span class="text-gray-500">{{ stats.chats?.closed ?? '—' }}</span>
          </div>
        </div>
      </div>

      <!-- Messages -->
      <div class="bg-white rounded-xl shadow p-5">
        <h3 class="text-sm font-semibold text-gray-500 mb-3">Сообщения</h3>
        <div class="space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">За сегодня</span>
            <span class="font-bold text-gray-800">{{ stats.messages?.today ?? '—' }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">За 24 часа</span>
            <span class="font-semibold text-blue-600">{{ stats.messages?.last_24h ?? '—' }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Сгенерировано AI</span>
            <span class="text-gray-600">{{ stats.messages?.ai_generated ?? '—' }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Ошибки</span>
            <span :class="(stats.messages?.failed ?? 0) > 0 ? 'font-semibold text-red-600' : 'text-gray-500'">
              {{ stats.messages?.failed ?? '—' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Clients & AI -->
      <div class="bg-white rounded-xl shadow p-5">
        <h3 class="text-sm font-semibold text-gray-500 mb-3">Клиенты и AI</h3>
        <div class="space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Всего клиентов</span>
            <span class="font-bold text-gray-800">{{ stats.clients?.total ?? '—' }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Активны сегодня</span>
            <span class="font-semibold text-green-600">{{ stats.clients?.active_today ?? '—' }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Заблокировано</span>
            <span class="text-gray-500">{{ stats.clients?.blocked ?? '—' }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Среднее время AI</span>
            <span :class="latencyClass">
              {{ stats.performance?.avg_ai_latency_ms != null ? (stats.performance.avg_ai_latency_ms / 1000).toFixed(2) + ' с' : '—' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Queue depths -->
    <div class="bg-white rounded-xl shadow p-5">
      <h3 class="text-sm font-semibold text-gray-500 mb-4">Очереди Celery</h3>
      <div class="grid grid-cols-3 gap-4">
        <div
          v-for="(depth, name) in queues.queues"
          :key="name"
          class="text-center p-4 rounded-lg border"
          :class="depth > 50 ? 'border-red-200 bg-red-50' : depth > 10 ? 'border-yellow-200 bg-yellow-50' : 'border-gray-100 bg-gray-50'"
        >
          <p class="text-2xl font-bold" :class="depth > 50 ? 'text-red-600' : depth > 10 ? 'text-yellow-600' : 'text-gray-700'">
            {{ depth }}
          </p>
          <p class="text-xs text-gray-500 mt-1 font-mono">{{ name }}</p>
          <p class="text-xs mt-0.5" :class="depth > 50 ? 'text-red-500' : depth > 10 ? 'text-yellow-500' : 'text-green-600'">
            {{ depth === 0 ? 'Пусто' : depth > 50 ? 'Перегрузка!' : depth > 10 ? 'Нагрузка' : 'Норма' }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { monitoringAPI } from '@/api'
import { format } from 'date-fns'

const health = ref({ status: 'ok', checks: {} })
const stats = ref({})
const queues = ref({ queues: { default: 0, messages: 0, ai: 0 } })
const lastUpdated = ref('—')

let interval = null

async function refresh() {
  try {
    const [healthRes, statsRes, queuesRes] = await Promise.all([
      monitoringAPI.health(),
      monitoringAPI.stats(),
      monitoringAPI.queues(),
    ])
    health.value = healthRes.data
    stats.value = statsRes.data
    queues.value = queuesRes.data
    lastUpdated.value = format(new Date(), 'HH:mm:ss')
  } catch (e) {
    // silently skip on network errors
  }
}

onMounted(() => {
  refresh()
  interval = setInterval(refresh, 30000)
})

onUnmounted(() => clearInterval(interval))

const latencyClass = computed(() => {
  const ms = stats.value.performance?.avg_ai_latency_ms ?? 0
  if (ms === 0) return 'text-gray-400'
  if (ms < 2000) return 'font-semibold text-green-600'
  if (ms < 3000) return 'font-semibold text-yellow-600'
  return 'font-semibold text-red-600'
})

function serviceIcon(name) {
  return { database: '🗄️', redis: '⚡', chromadb: '🧠', celery: '⚙️' }[name] || '🔧'
}

function serviceName(name) {
  return { database: 'PostgreSQL', redis: 'Redis', chromadb: 'ChromaDB', celery: 'Celery' }[name] || name
}
</script>
