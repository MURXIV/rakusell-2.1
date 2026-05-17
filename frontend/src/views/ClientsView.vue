<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-800">Клиенты</h2>
      <input
        v-model="search"
        type="text"
        placeholder="Поиск..."
        class="border border-gray-300 rounded-lg px-4 py-2 text-sm w-64 focus:outline-none focus:ring-2 focus:ring-green-500"
      />
    </div>

    <div class="bg-white rounded-xl shadow overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b">
          <tr>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">Имя</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">Телефон</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">Теги</th>
            <th class="text-left px-4 py-3 text-gray-600 font-medium">Последняя активность</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="client in clients"
            :key="client.id"
            @click="$router.push(`/app/clients/${client.id}`)"
            class="border-b hover:bg-gray-50 cursor-pointer"
          >
            <td class="px-4 py-3 font-medium text-gray-800">{{ client.name || '—' }}</td>
            <td class="px-4 py-3 text-gray-600">{{ client.phone }}</td>
            <td class="px-4 py-3">
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="tag in client.tags"
                  :key="tag"
                  class="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full"
                >{{ tag }}</span>
              </div>
            </td>
            <td class="px-4 py-3 text-gray-500">{{ client.last_seen ? formatDate(client.last_seen) : '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { clientsAPI } from '@/api'
import { format } from 'date-fns'

const clients = ref([])
const search = ref('')

async function fetchClients() {
  const { data } = await clientsAPI.list({ search: search.value || undefined })
  clients.value = data.results || data
}

watch(search, fetchClients)
onMounted(fetchClients)

function formatDate(dt) {
  return format(new Date(dt), 'dd.MM.yyyy HH:mm')
}
</script>
