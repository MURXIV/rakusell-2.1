<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-800">Пользователи</h2>
      <button @click="showCreate = true"
        class="text-white px-4 py-2 rounded-lg text-sm font-medium"
        style="background:linear-gradient(135deg,#0ABFB8,#08A89F)">
        + Добавить
      </button>
    </div>

    <div class="bg-white rounded-xl shadow overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b">
          <tr>
            <th class="text-left px-4 py-3 text-gray-500 font-medium">Логин</th>
            <th class="text-left px-4 py-3 text-gray-500 font-medium">Email</th>
            <th class="text-left px-4 py-3 text-gray-500 font-medium">Роль</th>
            <th class="text-left px-4 py-3 text-gray-500 font-medium">Статус</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-medium text-gray-800">{{ user.username }}</td>
            <td class="px-4 py-3 text-gray-600">{{ user.email || '—' }}</td>
            <td class="px-4 py-3">
              <span class="px-2 py-1 rounded-full text-xs font-medium"
                :class="user.role === 'admin' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'">
                {{ user.role === 'admin' ? 'Admin' : 'Manager' }}
              </span>
            </td>
            <td class="px-4 py-3">
              <span class="px-2 py-1 rounded-full text-xs font-medium"
                :class="user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
                {{ user.is_active ? 'Активен' : 'Заблокирован' }}
              </span>
            </td>
            <td class="px-4 py-3 text-right">
              <button @click="toggleActive(user)" class="text-xs text-gray-400 hover:text-gray-700 mr-3">
                {{ user.is_active ? 'Заблокировать' : 'Разблокировать' }}
              </button>
              <button @click="deleteUser(user)" class="text-xs text-red-400 hover:text-red-600">Удалить</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create modal -->
    <div v-if="showCreate" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
        <h3 class="text-lg font-bold mb-4">Новый пользователь</h3>
        <div class="space-y-3">
          <input v-model="form.username" placeholder="Логин" class="w-full border rounded-lg px-3 py-2 text-sm" />
          <input v-model="form.email" placeholder="Email" type="email" class="w-full border rounded-lg px-3 py-2 text-sm" />
          <input v-model="form.password" placeholder="Пароль" type="password" class="w-full border rounded-lg px-3 py-2 text-sm" />
          <select v-model="form.role" class="w-full border rounded-lg px-3 py-2 text-sm">
            <option value="manager">Manager</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        <div class="flex gap-2 mt-4">
          <button @click="createUser"
            class="flex-1 text-white py-2 rounded-lg text-sm font-medium"
            style="background:linear-gradient(135deg,#0ABFB8,#08A89F)">Создать</button>
          <button @click="showCreate = false" class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 rounded-lg text-sm">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const users = ref([])
const showCreate = ref(false)
const form = ref({ username: '', email: '', password: '', role: 'manager' })

async function fetchUsers() {
  const { data } = await api.get('/users/')
  users.value = data
}

async function createUser() {
  if (!form.value.username || !form.value.password) return
  await api.post('/users/', form.value)
  showCreate.value = false
  form.value = { username: '', email: '', password: '', role: 'manager' }
  fetchUsers()
}

async function toggleActive(user) {
  await api.patch(`/users/${user.id}/`, { is_active: !user.is_active })
  fetchUsers()
}

async function deleteUser(user) {
  if (!confirm(`Удалить пользователя ${user.username}?`)) return
  await api.delete(`/users/${user.id}/`)
  fetchUsers()
}

onMounted(fetchUsers)
</script>
