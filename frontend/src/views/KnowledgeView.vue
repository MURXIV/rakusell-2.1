<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-800">База знаний</h2>
      <button @click="showForm = true" class="px-4 py-2 rounded-lg text-sm font-medium text-white" style="background:linear-gradient(135deg,#0ABFB8,#08A89F)">
        + Добавить документ
      </button>
    </div>

    <div class="grid gap-4">
      <div v-for="doc in docs" :key="doc.id" class="bg-white rounded-xl shadow overflow-hidden">
        <div class="p-5 flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-1">
              <span class="text-lg">{{ docIcon(doc.doc_type) }}</span>
              <h3 class="font-semibold text-gray-800">{{ doc.title }}</h3>
              <span class="bg-gray-100 text-gray-600 text-xs px-2 py-0.5 rounded-full">{{ doc.doc_type }}</span>
              <span v-if="doc.is_indexed && doc.chunk_count > 0" class="bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded-full">Проиндексирован</span>
              <span v-else-if="!doc.is_indexed && doc.doc_type === 'url' && doc.chunk_count === 0" class="bg-red-100 text-red-700 text-xs px-2 py-0.5 rounded-full" title="Сайт заблокировал скачивание (Cloudflare/JS). Вставьте текст вручную.">⚠️ Ошибка скачивания</span>
              <span v-else class="bg-yellow-100 text-yellow-700 text-xs px-2 py-0.5 rounded-full">Ожидает</span>
            </div>
            <p class="text-sm text-gray-500">{{ doc.chunk_count }} чанков</p>
          </div>
          <div class="flex items-center gap-2 ml-4">
            <button
              v-if="doc.is_indexed && doc.chunk_count > 0"
              @click="toggleChunks(doc.id)"
              class="text-xs text-blue-500 hover:text-blue-700 border border-blue-200 rounded px-2 py-1"
            >
              {{ expandedDoc === doc.id ? 'Скрыть' : 'Эмбеддинги' }}
            </button>
            <button
              @click="reindexDoc(doc)"
              :disabled="reindexingId === doc.id"
              class="text-xs text-teal-600 hover:text-teal-800 border border-teal-200 rounded px-2 py-1 disabled:opacity-50"
              title="Переиндексировать документ"
            >
              {{ reindexingId === doc.id ? '⏳' : '🔄' }}
            </button>
            <button @click="deleteDoc(doc.id)" class="text-gray-400 hover:text-red-500">🗑️</button>
          </div>
        </div>

        <!-- Chunks viewer -->
        <div v-if="expandedDoc === doc.id" class="border-t bg-gray-50 px-5 py-4">
          <div v-if="loadingChunks" class="text-sm text-gray-400 py-2">Загрузка чанков...</div>
          <div v-else-if="chunks.length === 0" class="text-sm text-gray-400 py-2">Чанки не найдены</div>
          <div v-else class="space-y-3 max-h-96 overflow-y-auto">
            <div
              v-for="chunk in chunks"
              :key="chunk.id"
              class="bg-white rounded-lg border p-3 text-xs"
            >
              <div class="flex items-center justify-between mb-2 text-gray-400">
                <span class="font-mono">Чанк #{{ chunk.chunk_index + 1 }}</span>
                <span>{{ chunk.token_count }} токенов · <span class="font-mono text-gray-300">{{ chunk.chroma_id }}</span></span>
              </div>
              <p class="text-gray-700 leading-relaxed whitespace-pre-wrap">{{ chunk.chunk_text }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Upload modal -->
    <div v-if="showForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-6 w-full max-w-lg shadow-xl">
        <h3 class="text-lg font-semibold mb-4">Добавить документ</h3>
        <form @submit.prevent="uploadDoc" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Название</label>
            <input v-model="form.title" required class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Тип</label>
            <select v-model="form.doc_type" class="w-full border rounded-lg px-3 py-2 text-sm">
              <option value="faq">FAQ</option>
              <option value="text">Текст</option>
              <option value="pdf">PDF</option>
              <option value="url">URL страница</option>
            </select>
          </div>
          <div v-if="form.doc_type === 'faq' || form.doc_type === 'text'">
            <label class="block text-sm font-medium text-gray-700 mb-1">Содержимое</label>
            <textarea v-model="form.content" rows="6" class="w-full border rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-green-500"></textarea>
          </div>
          <div v-if="form.doc_type === 'pdf'">
            <label class="block text-sm font-medium text-gray-700 mb-1">PDF файл</label>
            <input type="file" accept=".pdf" @change="onFile" class="text-sm" />
          </div>
          <div v-if="form.doc_type === 'url'">
            <label class="block text-sm font-medium text-gray-700 mb-1">URL</label>
            <input v-model="form.source_url" type="url" placeholder="https://example.com/page" class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
            <p class="text-xs text-gray-400 mt-1">⚠️ Страница скачивается автоматически. Если сайт защищён Cloudflare или требует JS — вставьте текст вручную ниже.</p>
            <label class="block text-sm font-medium text-gray-700 mt-3 mb-1">Текст страницы (запасной вариант)</label>
            <textarea v-model="form.content" rows="5" placeholder="Вставьте текст вручную если автоскачивание не работает..." class="w-full border rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-green-500"></textarea>
          </div>
          <div class="flex justify-end gap-3">
            <button type="button" @click="showForm = false" class="px-4 py-2 text-sm text-gray-600">Отмена</button>
            <button type="submit" class="px-5 py-2 rounded-lg text-sm font-medium text-white" style="background:linear-gradient(135deg,#0ABFB8,#08A89F)">Загрузить</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { knowledgeAPI } from '@/api'

const docs = ref([])
const showForm = ref(false)
const form = ref({ title: '', doc_type: 'faq', content: '', file: null, source_url: '' })
const expandedDoc = ref(null)
const chunks = ref([])
const loadingChunks = ref(false)
const reindexingId = ref(null)

onMounted(async () => {
  const { data } = await knowledgeAPI.list()
  docs.value = data.results || data
})

async function toggleChunks(docId) {
  if (expandedDoc.value === docId) {
    expandedDoc.value = null
    chunks.value = []
    return
  }
  expandedDoc.value = docId
  loadingChunks.value = true
  try {
    const { data } = await knowledgeAPI.get(docId)
    chunks.value = data.embeddings || []
  } finally {
    loadingChunks.value = false
  }
}

function onFile(e) {
  form.value.file = e.target.files[0]
}

async function uploadDoc() {
  const fd = new FormData()
  fd.append('title', form.value.title)
  fd.append('doc_type', form.value.doc_type)
  if (form.value.content) fd.append('content', form.value.content)
  if (form.value.file) fd.append('file', form.value.file)
  if (form.value.source_url) fd.append('source_url', form.value.source_url)
  await knowledgeAPI.create(fd)
  const { data } = await knowledgeAPI.list()
  docs.value = data.results || data
  showForm.value = false
  form.value = { title: '', doc_type: 'faq', content: '', file: null, source_url: '' }
}

async function reindexDoc(doc) {
  reindexingId.value = doc.id
  try {
    await knowledgeAPI.reindex(doc.id)
    // Poll for updated chunk_count for up to 15 seconds
    for (let i = 0; i < 15; i++) {
      await new Promise(r => setTimeout(r, 1000))
      const { data } = await knowledgeAPI.get(doc.id)
      const target = docs.value.find(d => d.id === doc.id)
      if (target) {
        target.chunk_count = data.chunk_count
        target.is_indexed = data.is_indexed
      }
      if (data.chunk_count > 0) break
    }
  } catch (e) {
    alert('Ошибка переиндексации: ' + (e.response?.data?.detail || e.message))
  } finally {
    reindexingId.value = null
  }
}

async function deleteDoc(id) {
  if (!confirm('Удалить документ из базы знаний?')) return
  await knowledgeAPI.delete(id)
  docs.value = docs.value.filter(d => d.id !== id)
}

function docIcon(type) {
  return { faq: '❓', pdf: '📄', text: '📝', url: '🔗' }[type] || '📄'
}
</script>


