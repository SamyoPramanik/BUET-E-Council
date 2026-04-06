<template>
  <nav class="w-full py-4 px-8 flex items-center justify-between bg-white border-b border-gray-100 shadow-sm sticky top-0 z-50">
    <router-link 
      to="/" 
      class="text-2xl font-black tracking-tighter text-blue-600 hover:text-blue-700 transition-all active:scale-95"
    >
      BUET_Ecouncil
    </router-link>

    <div v-if="isAuthenticated" class="flex items-center gap-4">
      
      <button 
        v-if="userRole === 'admin'"
        @click="goToAdmin"
        class="hidden sm:flex items-center gap-2 px-4 py-2 text-sm font-bold text-gray-700 hover:bg-gray-100 rounded-xl transition-colors border border-gray-200"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        Admin Panel
      </button>

      <div class="relative" ref="dropdownRef">
        <button 
          @click="isDropdownOpen = !isDropdownOpen"
          class="w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-sm uppercase shadow-md hover:bg-blue-700 transition-transform active:scale-90"
        >
          {{ userInitials }}
        </button>

        <transition
          enter-active-class="transition duration-100 ease-out"
          enter-from-class="transform scale-95 opacity-0"
          enter-to-class="transform scale-100 opacity-100"
          leave-active-class="transition duration-75 ease-in"
          leave-from-class="transform scale-100 opacity-100"
          leave-to-class="transform scale-95 opacity-0"
        >
          <div 
            v-if="isDropdownOpen"
            class="absolute right-0 mt-3 w-64 bg-white rounded-2xl shadow-2xl border border-gray-100 py-2 z-[60]"
          >
            <div class="px-4 py-3 border-b border-gray-50 mb-2">
              <div class="flex items-center justify-between mb-1">
                <p class="text-[10px] text-gray-400 font-black uppercase tracking-widest">Account</p>
                <span 
                  class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-tighter"
                  :class="userRole === 'admin' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'"
                >
                  {{ userRole }}
                </span>
              </div>
              <p class="text-sm font-bold text-gray-900 truncate">{{ userEmail }}</p>
            </div>

            <router-link 
              to="/profile" 
              class="flex items-center gap-3 px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors"
              @click="isDropdownOpen = false"
            >
              Profile Settings
            </router-link>

            <button 
              @click="handleLogout"
              class="w-full flex items-center gap-3 px-4 py-2.5 text-sm font-medium text-red-600 hover:bg-red-50 transition-colors text-left"
            >
              Sign out
            </button>
          </div>
        </transition>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import { authState } from '../store/auth'; // Reactive store for dynamic updates

const router = useRouter();
const toast = useToast();

const isDropdownOpen = ref(false);
const dropdownRef = ref(null);

// Map reactive store to computed properties for the template
const isAuthenticated = computed(() => authState.isAuthenticated);
const userEmail = computed(() => authState.userEmail);
const userRole = computed(() => authState.userRole);

// Get initials from email
const userInitials = computed(() => {
  const email = userEmail.value || '??';
  return email.substring(0, 2).toUpperCase();
});

const goToAdmin = () => {
  window.open('/admin/', '_blank', 'noopener,noreferrer');
};

const handleLogout = () => {
  authState.clear(); // Clears localStorage and triggers UI update
  isDropdownOpen.value = false;
  toast.info("Logged out successfully");
  router.push('/sign-in');
};

// Handle closing when clicking outside the profile menu
const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isDropdownOpen.value = false;
  }
};

onMounted(() => {
  window.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  window.removeEventListener('click', handleClickOutside);
});
</script>