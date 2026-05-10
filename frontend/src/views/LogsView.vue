<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-800">Логи</h2>
      <div class="flex gap-3">
        <select v-model="typeFilter" @change="fetchLogs" class="border rounded-lg px-3 py-2 text-sm">
          <option value="">Все типы</option>
          <option value="webhook">Webhook</option>
          <option value="ai_request">AI запросы</option>
          <option value="ai_error">AI ошибки</option>
          <option value="api_error">API ошибки</option>
          <option value="message_sent">Отправлено</option>
          <option value="message_received">Получено</option>
        </select>
        <select v-model="levelFilter" @change="fetchLogs" class="border rounded-lg px-3 py-2 text-sm">
          <option value="">Все уровни</option>
          <option value="info">Info</option>
          <option value="warning">Warning</option>
          <option value="error">Error</option>
          <option value="critical">Critical</option>
        </select>
      </div>
    </div>

    <div class="bg-white rounded-xl shadow overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b">
          <tr>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">Время</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">Тип</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">Уровень</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">Сообщение</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id" class="border-b hover:bg-gray-50">
            <td class="px-4 py-3 text-gray-500 whitespace-nowrap">{{ formatDate(log.created_at) }}</td>
            <td class="px-4 py-3">
              <span class="bg-gray-100 text-gray-600 text-xs px-2 py-0.5 rounded-full">{{ log.log_type }}</span>
            </td>
            <td class="px-4 py-3">
              <span :class="levelClass(log.level)" class="text-xs px-2 py-0.5 rounded-full font-medium">
                {{ log.level }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-700 max-w-md truncate">{{ log.message }}</td>
          </tr>
        </tbody>
      </table>
      <div v-if="logs.length === 0" class="text-center py-12 text-gray-400">Логи не найдены</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { logsAPI } from '@/api'
import { format } from 'date-fns'

const logs = ref([])
const typeFilter = ref('')
const levelFilter = ref('')

async function fetchLogs() {
  const { data } = await logsAPI.list({
    log_type: typeFilter.value || undefined,
    level: levelFilter.value || undefined,
  })
  logs.value = data.results || data
}

onMounted(fetchLogs)

function formatDate(dt) {
  return format(new Date(dt), 'dd.MM HH:mm:ss')
}

function levelClass(level) {
  return {
    info: 'bg-blue-100 text-blue-700',
    warning: 'bg-yellow-100 text-yellow-700',
    error: 'bg-red-100 text-red-700',
    critical: 'bg-red-200 text-red-800',
  }[level] || 'bg-gray-100 text-gray-600'
}
</script>
