import { ref, onUnmounted } from 'vue'

export function useWebSocket(chatId) {
  const messages = ref([])
  const isConnected = ref(false)
  let ws = null
  let reconnectTimer = null

  function connect() {
    const token = localStorage.getItem('access_token')
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
    const wsBaseUrl = import.meta.env.VITE_WS_URL || apiUrl
      .replace(/^http/, 'ws')
      .replace(/\/api\/v1\/?$/, '')
    const url = `${wsBaseUrl}/ws/chats/${chatId}/?token=${encodeURIComponent(token || '')}`

    ws = new WebSocket(url)

    ws.onopen = () => {
      isConnected.value = true
      console.log(`WS connected: chat ${chatId}`)
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'message') {
        messages.value.push(data.data)
      }
    }

    ws.onclose = () => {
      isConnected.value = false
      // Reconnect after 3 seconds
      reconnectTimer = setTimeout(connect, 3000)
    }

    ws.onerror = (err) => {
      console.error('WebSocket error:', err)
      ws.close()
    }
  }

  function disconnect() {
    clearTimeout(reconnectTimer)
    if (ws) {
      ws.close()
      ws = null
    }
  }

  onUnmounted(disconnect)

  return { messages, isConnected, connect, disconnect }
}
