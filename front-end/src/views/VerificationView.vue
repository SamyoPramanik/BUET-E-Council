<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';         
import { useToast } from 'vue-toastification'; 
import { authState } from '../store/auth'; // Import the reactive store
import api from '../utils/api';

const otp = ref(['', '', '', '', '', '']);
const timer = ref(300); 
const isLoading = ref(false);
let interval = null;

const router = useRouter();
const toast = useToast();

const isComplete = computed(() => otp.value.every(v => v !== ''));

const formatTime = computed(() => {
  const mins = Math.floor(timer.value / 60);
  const secs = timer.value % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
});

// Auto-focus logic
const handleInput = (e, index) => {
  const val = e.target.value;
  // Ensure only numbers
  if (val && !/^\d+$/.test(val)) {
    otp.value[index] = '';
    return;
  }
  if (val && index < 5) {
    document.getElementById(`otp-${index + 1}`).focus();
  }
};

const handleDelete = (e, index) => {
  if (!otp.value[index] && index > 0) {
    document.getElementById(`otp-${index - 1}`).focus();
  }
};

const handlePaste = (e) => {
  const pasteData = e.clipboardData.getData('text').trim().slice(0, 6).split('');
  if (pasteData.length > 0) {
    pasteData.forEach((char, index) => {
      if (index < 6 && /^\d$/.test(char)) otp.value[index] = char;
    });
    // Focus the last filled box or the verify button
    const nextIndex = Math.min(pasteData.length, 5);
    document.getElementById(`otp-${nextIndex}`).focus();
  }
};

const startTimer = () => {
  timer.value = 300;
  interval = setInterval(() => {
    if (timer.value > 0) timer.value--;
    else clearInterval(interval);
  }, 1000);
};

const verifyOTP = async () => {
  const code = otp.value.join('');
  const email = localStorage.getItem('pending_email');

  if (!email) {
    toast.error("Session expired. Please sign in again.");
    router.push('/sign-in');
    return;
  }

  isLoading.value = true;
  try {
    const response = await api.post('/auth/verify-otp', {
      email: email,
      code: code
    });

    if (response.data.status === "success") {
      const { session_id, user_role } = response.data.data;

      // 1. Save all data to localStorage
      localStorage.setItem('session_id', session_id);
      localStorage.setItem('user_role', user_role);
      localStorage.setItem('user_email', email);

      // 2. Set the cookie for the FastAPI Admin interface
      document.cookie = `session_id=${session_id}; path=/; samesite=lax;`;

      // 3. TRIGGER REACTIVE UPDATE
      // This tells the NavBar to show the profile icon immediately
      authState.refresh(); 

      toast.success("Login successful!");
      localStorage.removeItem('pending_email');
      
      router.push('/'); 
    }
  } catch (error) {
    const errorMsg = error.response?.data?.detail || "Invalid or expired OTP.";
    toast.error(errorMsg);
    otp.value = ['', '', '', '', '', ''];
    document.getElementById('otp-0').focus();
  } finally {
    isLoading.value = false;
  }
};

const resendOTP = async () => {
  const email = localStorage.getItem('pending_email');
  try {
    await api.post('/auth/request-otp', { email });
    toast.info("A new code has been sent.");
    startTimer();
  } catch (error) {
    toast.error("Failed to resend OTP.");
  }
};

onMounted(() => {
  // If no email is pending, user shouldn't be here
  if (!localStorage.getItem('pending_email')) {
    router.push('/sign-in');
  }
  startTimer();
});

onUnmounted(() => clearInterval(interval));
</script>

<template>
  <div class="min-h-[85vh] flex flex-col items-center justify-center px-4">
    <div class="max-w-md w-full bg-white p-10 rounded-[2.5rem] shadow-2xl shadow-blue-100/50 border border-slate-100">
      
      <div class="text-center mb-10">
        <div class="w-16 h-16 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 class="text-3xl font-black text-slate-800">Verification</h2>
        <p class="text-slate-500 mt-2 font-medium">
          Enter the code sent to your email
        </p>
      </div>

      <div class="flex justify-center gap-3 mb-10" @paste="handlePaste">
        <input
          v-for="(digit, index) in otp"
          :key="index"
          :id="'otp-' + index"
          v-model="otp[index]"
          type="text"
          inputmode="numeric"
          maxlength="1"
          class="w-12 h-16 text-center text-2xl font-black border-2 rounded-2xl focus:border-blue-600 focus:ring-4 focus:ring-blue-50 outline-none transition-all"
          :class="otp[index] 
            ? 'border-blue-600 bg-white' 
            : 'border-slate-200 bg-slate-50'"
          @input="handleInput($event, index)"
          @keydown.delete="handleDelete($event, index)"
        />
      </div>

      <button 
        @click="verifyOTP"
        :disabled="!isComplete || isLoading"
        class="w-full py-4 rounded-2xl font-bold transition-all mb-6 flex items-center justify-center gap-2 shadow-lg"
        :class="isComplete && !isLoading 
          ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-blue-200' 
          : 'bg-slate-200 text-slate-400 cursor-not-allowed'"
      >
        <svg v-if="isLoading" class="animate-spin h-5 w-5" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
        </svg>
        <span>{{ isLoading ? 'Checking...' : 'Verify & Continue' }}</span>
      </button>

      <div class="text-center">
        <p v-if="timer > 0" class="text-sm text-slate-400 font-medium">
          Didn't get the code? Wait <span class="font-bold text-blue-600">{{ formatTime }}</span>
        </p>
        <button 
          v-else 
          @click="resendOTP"
          class="text-sm font-bold text-blue-600 hover:text-blue-800 transition-colors"
        >
          Resend Access Code
        </button>
      </div>
    </div>
  </div>
</template>