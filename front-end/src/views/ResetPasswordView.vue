<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useToast } from 'vue-toastification'
import axios from '../utils/api'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const token = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const showNew = ref(false)
const showConfirm = ref(false)
const isLoading = ref(false)
const done = ref(false)

onMounted(() => {
  token.value = route.query.token || ''
  if (!token.value) {
    toast.error("Invalid reset link.")
    router.push('/forgot-password')
  }
})

const handleReset = async () => {
  if (isLoading.value) return
  if (!newPassword.value || newPassword.value.length < 6) {
    toast.error("Password must be at least 6 characters.")
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    toast.error("Passwords do not match.")
    return
  }

  isLoading.value = true
  try {
    await axios.post('/auth/reset-password', {
      token: token.value,
      new_password: newPassword.value,
    })
    done.value = true
    toast.success("Password reset successfully!")
  } catch (error) {
    const msg = error.response?.data?.detail || "Reset failed. The link may have expired."
    toast.error(msg)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <main class="flex flex-col items-center justify-center pt-20 px-4 min-h-[80vh]">
    <div class="w-full max-w-md bg-white p-10 rounded-[2rem] shadow-2xl shadow-blue-100/50 border border-slate-100">

      <div class="text-center mb-10">
        <h2 class="text-3xl font-black text-slate-800 mb-2">New Password</h2>
        <p class="text-slate-500 font-medium text-sm">Choose a strong password for your account.</p>
      </div>

      <div v-if="!done">
        <!-- New password -->
        <div class="relative group mb-5">
          <input
            v-model="newPassword"
            :type="showNew ? 'text' : 'password'"
            id="new-password"
            placeholder=" "
            :disabled="isLoading"
            class="block w-full px-4 py-4 pr-12 text-slate-900 bg-transparent border-2 border-slate-200 rounded-2xl appearance-none focus:outline-none focus:border-blue-500 peer transition-all disabled:bg-slate-50"
          />
          <label for="new-password" class="absolute text-slate-400 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-white px-2 peer-focus:text-blue-500 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:scale-75 peer-focus:-translate-y-4 left-3 pointer-events-none font-bold">
            New Password
          </label>
          <button type="button" @click="showNew = !showNew" class="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600" tabindex="-1">
            <svg v-if="!showNew" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/></svg>
          </button>
        </div>

        <!-- Confirm password -->
        <div class="relative group mb-8">
          <input
            v-model="confirmPassword"
            @keyup.enter="handleReset"
            :type="showConfirm ? 'text' : 'password'"
            id="confirm-password"
            placeholder=" "
            :disabled="isLoading"
            class="block w-full px-4 py-4 pr-12 text-slate-900 bg-transparent border-2 border-slate-200 rounded-2xl appearance-none focus:outline-none focus:border-blue-500 peer transition-all disabled:bg-slate-50"
          />
          <label for="confirm-password" class="absolute text-slate-400 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-white px-2 peer-focus:text-blue-500 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:scale-75 peer-focus:-translate-y-4 left-3 pointer-events-none font-bold">
            Confirm Password
          </label>
          <button type="button" @click="showConfirm = !showConfirm" class="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600" tabindex="-1">
            <svg v-if="!showConfirm" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/></svg>
          </button>
        </div>

        <button
          @click="handleReset"
          :disabled="isLoading"
          class="w-full bg-blue-600 text-white py-4 rounded-2xl font-bold hover:bg-blue-700 transition-all disabled:bg-blue-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          <svg v-if="isLoading" class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
          </svg>
          <span>{{ isLoading ? 'Updating…' : 'Set New Password' }}</span>
        </button>
      </div>

      <div v-else class="text-center">
        <div class="text-green-500 text-5xl mb-4">✓</div>
        <p class="text-slate-700 font-semibold mb-4">Password updated successfully!</p>
        <router-link to="/sign-in" class="bg-blue-600 text-white px-6 py-3 rounded-2xl font-bold hover:bg-blue-700 transition-all">
          Sign In
        </router-link>
      </div>
    </div>
  </main>
</template>
