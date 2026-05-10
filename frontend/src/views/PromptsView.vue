<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-800">Промпты</h2>
      <button
        @click="showForm = true"
        class="px-4 py-2 rounded-lg text-sm font-medium text-white" style="background:linear-gradient(135deg,#0ABFB8,#08A89F)"
      >
        + Новый промпт
      </button>
    </div>

    <div class="grid gap-4">
      <div
        v-for="prompt in prompts"
        :key="prompt.id"
        class="bg-white rounded-xl shadow p-5"
      >
        <div class="flex items-start justify-between">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <h3 class="font-semibold text-gray-800">{{ prompt.name }}</h3>
              <span class="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full">{{ prompt.scenario }}</span>
              <span v-if="prompt.is_active" class="bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded-full">Активный</span>
              <span v-if="prompt.is_ab_test" class="bg-purple-100 text-purple-700 text-xs px-2 py-0.5 rounded-full">A/B</span>
            </div>
            <p class="text-sm text-gray-500 line-clamp-2">{{ prompt.system_prompt }}</p>
          </div>
          <div class="flex gap-2 ml-4">
            <button @click="editPrompt(prompt)" class="text-gray-400 hover:text-blue-500 text-sm">✏️</button>
            <button @click="deletePrompt(prompt.id)" class="text-gray-400 hover:text-red-500 text-sm">🗑️</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showForm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-6 w-full max-w-2xl shadow-xl">
        <h3 class="text-lg font-semibold mb-4">{{ editing ? 'Редактировать' : 'Новый' }} промпт</h3>
        <form @submit.prevent="savePrompt" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Название</label>
            <input v-model="form.name" required class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
          </div>
          <div class="flex gap-4">
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-1">Сценарий</label>
              <select v-model="form.scenario" class="w-full border rounded-lg px-3 py-2 text-sm">
                <option value="general">General</option>
                <option value="sales">Sales</option>
                <option value="support">Support</option>
              </select>
            </div>
            <div class="flex items-end gap-4">
              <label class="flex items-center gap-2 text-sm">
                <input type="checkbox" v-model="form.is_active" class="rounded" />
                Активный
              </label>
              <label class="flex items-center gap-2 text-sm">
                <input type="checkbox" v-model="form.is_ab_test" class="rounded" />
                A/B тест
              </label>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">System Prompt</label>
            <textarea
              v-model="form.system_prompt"
              required
              rows="8"
              class="w-full border rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="You are a helpful assistant..."
            ></textarea>
          </div>
          <div class="flex justify-end gap-3">
            <button type="button" @click="closeForm" class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800">Отмена</button>
            <button type="submit" class="px-5 py-2 rounded-lg text-sm font-medium text-white" style="background:linear-gradient(135deg,#0ABFB8,#08A89F)">Сохранить</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { promptsAPI } from '@/api'

const prompts = ref([])
const showForm = ref(false)
const editing = ref(null)
const form = ref({ name: '', scenario: 'general', system_prompt: '', is_active: false, is_ab_test: false })

onMounted(async () => {
  const { data } = await promptsAPI.list()
  prompts.value = data.results || data
})

function editPrompt(p) {
  editing.value = p.id
  form.value = { ...p }
  showForm.value = true
}

async function savePrompt() {
  if (editing.value) {
    await promptsAPI.update(editing.value, form.value)
  } else {
    await promptsAPI.create(form.value)
  }
  const { data } = await promptsAPI.list()
  prompts.value = data.results || data
  closeForm()
}

async function deletePrompt(id) {
  if (!confirm('Удалить промпт?')) return
  await promptsAPI.delete(id)
  prompts.value = prompts.value.filter(p => p.id !== id)
}

function closeForm() {
  showForm.value = false
  editing.value = null
  form.value = { name: '', scenario: 'general', system_prompt: '', is_active: false, is_ab_test: false }
}
</script>


