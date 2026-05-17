<template>
  <div class="p-6 max-w-3xl">
    <button @click="$router.back()" class="text-gray-400 hover:text-gray-600 mb-4 flex items-center gap-1 text-sm">
      ← Назад
    </button>

    <div v-if="client" class="space-y-6">
      <div class="bg-white rounded-xl shadow p-6">
        <div class="flex items-start justify-between gap-4 mb-4">
          <h2 class="text-xl font-bold text-gray-800">{{ client.name || client.phone }}</h2>
          <button
            @click="toggleBot"
            :disabled="saving"
            class="inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-semibold transition-colors disabled:opacity-50"
            :class="client.is_blocked ? 'border-red-200 bg-red-50 text-red-700' : 'border-green-200 bg-green-50 text-green-700'"
            :title="client.is_blocked ? 'Включить автоответы' : 'Отключить автоответы'"
          >
            <span
              class="inline-block h-3 w-3 rounded-full"
              :class="client.is_blocked ? 'bg-red-500' : 'bg-green-500'"
            ></span>
            {{ client.is_blocked ? 'Бот выключен' : 'Бот включён' }}
          </button>
        </div>
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p class="text-gray-400 text-xs mb-1">Телефон</p>
            <p class="font-medium">{{ client.phone }}</p>
          </div>
          <div>
            <p class="text-gray-400 text-xs mb-1">Chat ID</p>
            <p class="font-mono text-xs">{{ client.chat_id }}</p>
          </div>
          <div>
            <p class="text-gray-400 text-xs mb-1">Последняя активность</p>
            <p>{{ client.last_seen ? formatDate(client.last_seen) : '—' }}</p>
          </div>
          <div>
            <p class="text-gray-400 text-xs mb-1">Автоответы</p>
            <span :class="client.is_blocked ? 'text-red-600' : 'text-green-600'" class="font-medium">
              {{ client.is_blocked ? 'Выключены' : 'Включены' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Tags -->
      <div class="bg-white rounded-xl shadow p-6">
        <h3 class="font-semibold text-gray-700 mb-3">Теги</h3>
        <div class="flex flex-wrap gap-2 mb-3">
          <span
            v-for="tag in client.tags"
            :key="tag"
            class="bg-blue-100 text-blue-700 text-sm px-3 py-1 rounded-full flex items-center gap-1"
          >
            {{ tag }}
            <button @click="removeTag(tag)" class="text-blue-400 hover:text-blue-700 ml-1">×</button>
          </span>
        </div>
        <div class="flex gap-2">
          <input
            v-model="newTag"
            @keyup.enter="addTag"
            type="text"
            placeholder="Добавить тег..."
            class="border rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          />
          <button @click="addTag" class="bg-blue-500 text-white px-3 py-1.5 rounded-lg text-sm">+</button>
        </div>
      </div>

      <!-- Memory -->
      <div class="bg-white rounded-xl shadow p-6">
        <h3 class="font-semibold text-gray-700 mb-3">Память AI</h3>
        <textarea
          v-model="client.context_summary"
          rows="4"
          class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          placeholder="Контекст и предпочтения клиента..."
        ></textarea>
        <button @click="saveClient" class="mt-3 px-4 py-2 rounded-lg text-sm text-white" style="background:linear-gradient(135deg,#0ABFB8,#08A89F)">
          Сохранить
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { clientsAPI } from '@/api'
import { format } from 'date-fns'

const route = useRoute()
const client = ref(null)
const newTag = ref('')
const saving = ref(false)

onMounted(async () => {
  const { data } = await clientsAPI.get(route.params.id)
  client.value = data
})

function addTag() {
  const tag = newTag.value.trim()
  if (tag && !client.value.tags.includes(tag)) {
    client.value.tags.push(tag)
    newTag.value = ''
  }
}

function removeTag(tag) {
  client.value.tags = client.value.tags.filter(t => t !== tag)
}

async function saveClient() {
  saving.value = true
  try {
    await clientsAPI.update(client.value.id, {
      tags: client.value.tags,
      context_summary: client.value.context_summary,
      preferences: client.value.preferences,
      is_blocked: client.value.is_blocked,
    })
  } finally {
    saving.value = false
  }
}

async function toggleBot() {
  if (!client.value || saving.value) return
  saving.value = true
  try {
    const nextBlocked = !client.value.is_blocked
    await clientsAPI.update(client.value.id, { is_blocked: nextBlocked })
    client.value.is_blocked = nextBlocked
  } finally {
    saving.value = false
  }
}

function formatDate(dt) {
  return format(new Date(dt), 'dd.MM.yyyy HH:mm')
}
</script>


