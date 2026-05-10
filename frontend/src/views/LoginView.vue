<template>
  <div class="min-h-screen flex" style="background:linear-gradient(135deg,#0ABFB8 0%,#08A89F 50%,#F5A623 100%)">

    <!-- Left branding panel -->
    <div class="hidden lg:flex flex-col justify-center items-center flex-1 px-12">
      <div class="text-5xl font-extrabold tracking-tight mb-4">
        <span class="text-white">Raku</span><span style="color:#FDE68A">sell</span>
      </div>
      <p class="text-white/80 text-lg font-medium text-center max-w-xs">
        AI-powered sales assistant for WhatsApp
      </p>
      <div class="mt-10 grid grid-cols-3 gap-4 opacity-70">
        <div v-for="i in 6" :key="i" class="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur"></div>
      </div>
    </div>

    <!-- Login card -->
    <div class="flex items-center justify-center w-full lg:w-auto lg:min-w-[440px] p-6">
      <div class="bg-white rounded-3xl shadow-2xl p-8 w-full max-w-sm">

        <div class="mb-8">
          <div class="text-2xl font-extrabold tracking-tight mb-1">
            <span style="color:#0ABFB8">Raku</span><span style="color:#F5A623">sell</span>
          </div>
          <p class="text-gray-400 text-sm">Войдите в панель управления</p>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-gray-500 mb-1.5 uppercase tracking-wide">Логин</label>
            <input
              v-model="form.username"
              type="text"
              required
              class="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none transition-all"
              style="focus:border-color:#0ABFB8"
              placeholder="admin"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-500 mb-1.5 uppercase tracking-wide">Пароль</label>
            <input
              v-model="form.password"
              type="password"
              required
              class="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none transition-all"
              placeholder="••••••••"
            />
          </div>

          <p v-if="error" class="text-red-500 text-xs font-medium">{{ error }}</p>

          <button
            type="submit"
            :disabled="loading"
            class="w-full text-white font-semibold py-2.5 rounded-xl transition-all disabled:opacity-50 text-sm"
            style="background:linear-gradient(135deg,#0ABFB8,#08A89F)"
          >
            {{ loading ? 'Входим...' : 'Войти' }}
          </button>
        </form>

        <div class="mt-6 pt-5 border-t border-gray-100">
          <p class="text-xs text-gray-400 mb-2 font-medium">Сброс пароля</p>
          <div class="flex gap-2">
            <input
              v-model="newPassword"
              type="password"
              placeholder="Новый пароль"
              class="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-xs focus:outline-none"
            />
            <button
              type="button"
              @click="resetPassword"
              :disabled="resetting"
              class="text-white px-3 py-2 rounded-lg text-xs font-medium transition-all disabled:opacity-50"
              style="background:#F5A623"
            >
              {{ resetting ? '...' : 'Сброс' }}
            </button>
          </div>
          <p v-if="resetMsg" class="text-xs mt-1.5" :class="resetMsg.includes('Ошибка') ? 'text-red-500' : 'text-teal-600'">{{ resetMsg }}</p>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const auth = useAuthStore()
const router = useRouter()

const form = ref({ username: '', password: '' })
const loading = ref(false)
const error = ref('')
const newPassword = ref('')
const resetting = ref(false)
const resetMsg = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    await auth.login(form.value.username, form.value.password)
    router.push('/chats')
  } catch (e) {
    error.value = 'Неверный логин или пароль'
  } finally {
    loading.value = false
  }
}

async function resetPassword() {
  if (!newPassword.value || newPassword.value.length < 6) {
    resetMsg.value = 'Минимум 6 символов'
    return
  }
  resetting.value = true
  resetMsg.value = ''
  try {
    await axios.post('http://localhost:8000/api/v1/users/reset-password/', {
      username: form.value.username || 'admin',
      new_password: newPassword.value,
    })
    resetMsg.value = 'Пароль сброшен — войдите с новым паролем'
    newPassword.value = ''
  } catch (e) {
    resetMsg.value = 'Ошибка. Используй команду в терминале.'
  } finally {
    resetting.value = false
  }
}
</script>
