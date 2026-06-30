<script setup>
import { ref } from 'vue'
import { useToast } from 'vue-toastification'
import axios from '../utils/api'

const email = ref('')
const isLoading = ref(false)
const sent = ref(false)
const toast = useToast()

const handleSubmit = async () => {
  if (isLoading.value) return
  if (!email.value) {
    toast.error("Please enter your email address.")
    return
  }

  isLoading.value = true
  try {
    await axios.post('/auth/forgot-password', { email: email.value })
    sent.value = true
  } catch {
    toast.error("Something went wrong. Please try again.")
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <main class="flex flex-col items-center justify-center pt-20 px-4 min-h-[80vh]">
    <div class="w-full max-w-md bg-white p-10 rounded-[2rem] shadow-2xl shadow-blue-100/50 border border-slate-100">

      <div class="text-center mb-10">
        <h2 class="text-3xl font-black text-slate-800 mb-2">Reset Password</h2>
        <p class="text-slate-500 font-medium text-sm">Enter your email to receive a reset link.</p>
      </div>

      <div v-if="!sent">
        <div class="relative group mb-8">
          <input
            v-model="email"
            @keyup.enter="handleSubmit"
            type="email"
            id="email"
            placeholder=" "
            :disabled="isLoading"
            class="block w-full px-4 py-4 text-slate-900 bg-transparent border-2 border-slate-200 rounded-2xl appearance-none focus:outline-none focus:border-blue-500 peer transition-all disabled:bg-slate-50"
          />
          <label for="email" class="absolute text-slate-400 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-white px-2 peer-focus:text-blue-500 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:scale-75 peer-focus:-translate-y-4 left-3 pointer-events-none font-bold">
            Email Address
          </label>
        </div>

        <button
          @click="handleSubmit"
          :disabled="isLoading"
          class="w-full bg-blue-600 text-white py-4 rounded-2xl font-bold hover:bg-blue-700 transition-all disabled:bg-blue-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          <svg v-if="isLoading" class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
          </svg>
          <span>{{ isLoading ? 'Sending…' : 'Send Reset Link' }}</span>
        </button>
      </div>

      <div v-else class="text-center">
        <div class="text-green-500 text-5xl mb-4">✓</div>
        <p class="text-slate-700 font-semibold mb-2">Check your inbox</p>
        <p class="text-slate-500 text-sm">If <strong>{{ email }}</strong> is registered, a reset link has been sent. It expires in 1 hour.</p>
      </div>

      <div class="mt-8 text-center">
        <router-link to="/sign-in" class="text-sm text-blue-500 hover:text-blue-700 font-medium">
          Back to Sign In
        </router-link>
      </div>
    </div>
  </main>
</template>
