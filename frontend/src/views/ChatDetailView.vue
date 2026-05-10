<template>
  <div class="flex h-full">
    <!-- Messages panel -->
    <div class="flex-1 flex flex-col">
      <!-- Header -->
      <div class="bg-white border-b px-6 py-4 flex items-center gap-4">
        <button @click="$router.back()" class="text-gray-400 hover:text-gray-600">←</button>
        <div>
          <h3 class="font-semibold text-gray-800">{{ chat?.client?.name || chat?.client?.phone }}</h3>
          <p class="text-xs text-gray-400">{{ chat?.client?.phone }}</p>
        </div>
        <div class="ml-auto flex items-center gap-2">
          <span :class="wsConnected ? 'bg-green-400' : 'bg-gray-300'" class="w-2 h-2 rounded-full"></span>
          <span class="text-xs text-gray-400">{{ wsConnected ? 'Live' : 'Offline' }}</span>
        </div>
      </div>

      <!-- Messages -->
      <div ref="messagesEl" class="flex-1 overflow-y-auto p-6 space-y-3 bg-gray-50">
        <div
          v-for="msg in allMessages"
          :key="msg.id"
          :class="msg.direction === 'outbound' ? 'flex justify-end' : 'flex justify-start'"
        >
          <div
            :class="[
              'max-w-xs lg:max-w-md px-4 py-2 rounded-2xl text-sm',
              msg.direction === 'outbound'
                ? 'text-white rounded-br-sm'
                : 'bg-white text-gray-800 shadow-sm rounded-bl-sm'
            ]"
            :style="msg.direction === 'outbound' ? 'background:linear-gradient(135deg,#0ABFB8,#08A89F)' : ''"
          >
            <p>{{ msg.content }}</p>
            <p :class="msg.direction === 'outbound' ? 'text-teal-100' : 'text-gray-400'" class="text-xs mt-1">
              {{ formatTime(msg.created_at) }}
              <span v-if="msg.is_ai_generated" class="ml-1">🤖</span>
            </p>
          </div>
        </div>
      </div>

      <!-- Input -->
      <div class="bg-white border-t px-6 py-4 flex gap-3">
        <input
          v-model="newMessage"
          @keyup.enter="sendMessage"
          type="text"
          placeholder="Написать сообщение..."
          class="flex-1 border border-gray-200 rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-400"
        />
        <button
          @click="sendMessage"
          :disabled="!newMessage.trim() || sending"
          class="text-white px-5 py-2 rounded-xl text-sm font-semibold transition-all disabled:opacity-50"
          style="background:linear-gradient(135deg,#0ABFB8,#08A89F)"
        >
          Отправить
        </button>
      </div>
    </div>

    <!-- Client sidebar -->
    <div v-if="chat?.client" class="w-72 bg-white border-l p-5 overflow-y-auto">
      <h4 class="font-semibold text-gray-700 mb-4">Клиент</h4>
      <div class="space-y-3 text-sm">
        <div>
          <p class="text-gray-400 text-xs">Имя</p>
          <p class="font-medium">{{ chat.client.name || '—' }}</p>
        </div>
        <div>
          <p class="text-gray-400 text-xs">Телефон</p>
          <p class="font-medium">{{ chat.client.phone }}</p>
        </div>
        <div>
          <p class="text-gray-400 text-xs mb-1">Теги</p>
          <div class="flex flex-wrap gap-1">
            <span
              v-for="tag in chat.client.tags"
              :key="tag"
              class="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full"
            >{{ tag }}</span>
            <span v-if="!chat.client.tags?.length" class="text-gray-400">Нет тегов</span>
          </div>
        </div>
        <div v-if="chat.client.context_summary">
          <p class="text-gray-400 text-xs mb-1">Память AI</p>
          <p class="text-gray-600 text-xs bg-gray-50 p-2 rounded">{{ chat.client.context_summary }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRoute } from 'vue-router'
import { chatsAPI, messagesAPI } from '@/api'
import { useWebSocket } from '@/composables/useWebSocket'
import { format } from 'date-fns'

const route = useRoute()
const chatId = route.params.id

const chat = ref(null)
const historicMessages = ref([])
const newMessage = ref('')
const sending = ref(false)
const messagesEl = ref(null)

const { messages: wsMessages, isConnected: wsConnected, connect } = useWebSocket(chatId)

const allMessages = computed(() => [...historicMessages.value, ...wsMessages.value])

onMounted(async () => {
  const [chatRes, msgRes] = await Promise.all([
    chatsAPI.get(chatId),
    chatsAPI.messages(chatId),
  ])
  chat.value = chatRes.data
  historicMessages.value = msgRes.data.results || msgRes.data
  connect()
  await nextTick()
  scrollToBottom()

  // Polling fallback — обновляем каждые 3 секунды
  setInterval(async () => {
    const res = await chatsAPI.messages(chatId)
    const msgs = res.data.results || res.data
    if (msgs.length !== historicMessages.value.length) {
      historicMessages.value = msgs
      await nextTick()
      scrollToBottom()
    }
  }, 3000)
})

async function sendMessage() {
  if (!newMessage.value.trim() || sending.value) return
  sending.value = true
  try {
    await messagesAPI.send({
      client_id: chat.value.client.id,
      content: newMessage.value.trim(),
    })
    newMessage.value = ''
    await nextTick()
    scrollToBottom()
  } finally {
    sending.value = false
  }
}

function scrollToBottom() {
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}

function formatTime(dt) {
  return format(new Date(dt), 'HH:mm')
}
</script>
