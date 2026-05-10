<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-800">Чаты</h2>
      <div class="flex flex-wrap gap-3">
        <input
          v-model="search"
          type="text"
          placeholder="Поиск по номеру или имени..."
          class="border border-gray-300 rounded-lg px-4 py-2 text-sm w-64 focus:outline-none focus:ring-2 focus:ring-green-500"
        />
        <select
          v-model="statusFilter"
          class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none"
        >
          <option value="">Все статусы</option>
          <option value="active">Активные</option>
          <option value="closed">Закрытые</option>
          <option value="pending">Ожидающие</option>
        </select>
        <input
          v-model="dateFrom"
          type="date"
          class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          title="Дата от"
        />
        <input
          v-model="dateTo"
          type="date"
          class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          title="Дата до"
        />
        <button
          v-if="dateFrom || dateTo"
          @click="dateFrom = ''; dateTo = ''"
          class="text-sm text-gray-400 hover:text-gray-600 px-2"
          title="Сбросить даты"
        >✕</button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">Загрузка...</div>

    <div v-else class="bg-white rounded-xl shadow overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b">
          <tr>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">Клиент</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">Телефон</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">Статус</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">Последнее сообщение</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">Непрочитанных</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="chat in chats"
            :key="chat.id"
            @click="$router.push(`/chats/${chat.id}`)"
            class="border-b hover:bg-gray-50 cursor-pointer transition-colors"
          >
            <td class="px-4 py-3 font-medium text-gray-800">
              {{ chat.client.name || 'Без имени' }}
            </td>
            <td class="px-4 py-3 text-gray-600">{{ chat.client.phone }}</td>
            <td class="px-4 py-3">
              <span :class="statusClass(chat.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                {{ statusLabel(chat.status) }}
              </span>
            </td>
            <td class="px-4 py-3 text-gray-500">
              {{ chat.last_message_at ? formatDate(chat.last_message_at) : '—' }}
            </td>
            <td class="px-4 py-3">
              <span v-if="chat.unread_count > 0" class="bg-green-500 text-white text-xs rounded-full px-2 py-0.5">
                {{ chat.unread_count }}
              </span>
              <span v-else class="text-gray-400">0</span>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="chats.length === 0" class="text-center py-12 text-gray-400">
        Чаты не найдены
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { chatsAPI } from '@/api'
import { format } from 'date-fns'

const chats = ref([])
const loading = ref(false)
const search = ref('')
const statusFilter = ref('')
const dateFrom = ref('')
const dateTo = ref('')

async function fetchChats() {
  loading.value = true
  try {
    const { data } = await chatsAPI.list({
      search: search.value || undefined,
      status: statusFilter.value || undefined,
      date_from: dateFrom.value ? dateFrom.value + 'T00:00:00' : undefined,
      date_to: dateTo.value ? dateTo.value + 'T23:59:59' : undefined,
    })
    chats.value = data.results || data
  } finally {
    loading.value = false
  }
}

watch([search, statusFilter, dateFrom, dateTo], fetchChats, { debounce: 300 })
onMounted(fetchChats)

function formatDate(dt) {
  return format(new Date(dt), 'dd.MM.yyyy HH:mm')
}

function statusClass(s) {
  return {
    active: 'bg-green-100 text-green-700',
    closed: 'bg-gray-100 text-gray-600',
    pending: 'bg-yellow-100 text-yellow-700',
  }[s] || 'bg-gray-100 text-gray-600'
}

function statusLabel(s) {
  return { active: 'Активный', closed: 'Закрыт', pending: 'Ожидание' }[s] || s
}
</script>
