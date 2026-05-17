<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-800">Статус системы</h2>
      <div class="flex items-center gap-3">
        <span class="text-xs text-gray-400">Обновлено: {{ lastUpdated || '-' }}</span>
        <button
          @click="refresh"
          :disabled="loading"
          class="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-lg disabled:opacity-60"
        >
          {{ loading ? 'Проверяю...' : 'Обновить' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
      {{ error }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4 mb-6">
      <div
        v-for="(check, name) in health.checks"
        :key="name"
        class="bg-white rounded-xl shadow p-4"
      >
        <p class="text-xs text-gray-500 mb-1">{{ serviceName(name) }}</p>
        <div class="flex items-center gap-2">
          <span class="inline-block w-2.5 h-2.5 rounded-full" :class="statusDot(check.status)"></span>
          <span class="text-sm font-semibold" :class="statusText(check.status)">
            {{ check.status === 'ok' ? 'OK' : 'Ошибка' }}
          </span>
          <span v-if="check.workers !== undefined" class="text-xs text-gray-400">({{ check.workers }})</span>
        </div>
        <p v-if="check.detail" class="text-xs text-red-500 mt-2 break-words">{{ check.detail }}</p>
      </div>

      <div class="bg-white rounded-xl shadow p-4">
        <p class="text-xs text-gray-500 mb-1">Система</p>
        <div class="flex items-center gap-2">
          <span class="inline-block w-2.5 h-2.5 rounded-full" :class="health.status === 'ok' ? 'bg-green-500' : 'bg-yellow-400'"></span>
          <span class="text-sm font-semibold" :class="health.status === 'ok' ? 'text-green-700' : 'text-yellow-700'">
            {{ health.status === 'ok' ? 'Работает' : 'Есть проблемы' }}
          </span>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
      <section class="bg-white rounded-xl shadow p-5">
        <h3 class="text-sm font-semibold text-gray-500 mb-3">Чаты</h3>
        <Metric label="Всего" :value="stats.chats?.total" strong />
        <Metric label="Активных" :value="stats.chats?.active" />
        <Metric label="Ожидают" :value="stats.chats?.pending" />
        <Metric label="Закрытых" :value="stats.chats?.closed" />
      </section>

      <section class="bg-white rounded-xl shadow p-5">
        <h3 class="text-sm font-semibold text-gray-500 mb-3">Сообщения</h3>
        <Metric label="За сегодня" :value="stats.messages?.today" strong />
        <Metric label="За 24 часа" :value="stats.messages?.last_24h" />
        <Metric label="Сгенерировано AI" :value="stats.messages?.ai_generated" />
        <Metric label="Ошибки" :value="stats.messages?.failed" />
      </section>

      <section class="bg-white rounded-xl shadow p-5">
        <h3 class="text-sm font-semibold text-gray-500 mb-3">Клиенты и AI</h3>
        <Metric label="Всего клиентов" :value="stats.clients?.total" strong />
        <Metric label="Активны сегодня" :value="stats.clients?.active_today" />
        <Metric label="Заблокировано" :value="stats.clients?.blocked" />
        <Metric label="Среднее время AI" :value="avgLatency" />
      </section>
    </div>

    <section class="bg-white rounded-xl shadow p-5">
      <h3 class="text-sm font-semibold text-gray-500 mb-4">Очереди Celery</h3>
      <div class="grid grid-cols-3 gap-4">
        <div
          v-for="(depth, name) in queues.queues"
          :key="name"
          class="text-center p-4 rounded-lg border border-gray-100 bg-gray-50"
        >
          <p class="text-2xl font-bold text-gray-800">{{ depth }}</p>
          <p class="text-xs text-gray-500 mt-1 font-mono">{{ name }}</p>
          <p class="text-xs mt-0.5" :class="depth === 0 ? 'text-green-600' : 'text-yellow-600'">
            {{ depth === 0 ? 'Пусто' : 'Есть задачи' }}
          </p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, onUnmounted, ref } from 'vue'
import { monitoringAPI } from '@/api'
import { format } from 'date-fns'

const Metric = defineComponent({
  props: {
    label: String,
    value: [String, Number],
    strong: Boolean,
  },
  setup(props) {
    return () => h('div', { class: 'flex justify-between text-sm mb-2' }, [
      h('span', { class: 'text-gray-600' }, props.label),
      h('span', { class: props.strong ? 'font-bold text-gray-800' : 'text-gray-700' }, props.value ?? '-'),
    ])
  },
})

const health = ref({ status: 'unknown', checks: {} })
const stats = ref({})
const queues = ref({ queues: { default: 0, messages: 0, ai: 0 } })
const lastUpdated = ref('')
const loading = ref(false)
const error = ref('')

let interval = null

async function refresh() {
  loading.value = true
  error.value = ''

  const [healthRes, statsRes, queuesRes] = await Promise.allSettled([
    monitoringAPI.health(),
    monitoringAPI.stats(),
    monitoringAPI.queues(),
  ])

  if (healthRes.status === 'fulfilled') {
    health.value = healthRes.value.data
  }
  if (statsRes.status === 'fulfilled') {
    stats.value = statsRes.value.data
  }
  if (queuesRes.status === 'fulfilled') {
    queues.value = queuesRes.value.data
  }

  const failed = [healthRes, statsRes, queuesRes].filter((result) => result.status === 'rejected')
  if (failed.length) {
    error.value = failed[0].reason?.response?.data?.error || failed[0].reason?.message || 'Не удалось загрузить часть статуса'
  }

  lastUpdated.value = format(new Date(), 'HH:mm:ss')
  loading.value = false
}

onMounted(() => {
  refresh()
  interval = setInterval(refresh, 30000)
})

onUnmounted(() => clearInterval(interval))

const avgLatency = computed(() => {
  const ms = stats.value.performance?.avg_ai_latency_ms
  return ms != null ? `${(ms / 1000).toFixed(2)} с` : '-'
})

function statusDot(status) {
  return status === 'ok' ? 'bg-green-500' : 'bg-red-500'
}

function statusText(status) {
  return status === 'ok' ? 'text-green-700' : 'text-red-700'
}

function serviceName(name) {
  return { database: 'PostgreSQL', redis: 'Redis', chromadb: 'ChromaDB', celery: 'Celery' }[name] || name
}
</script>
