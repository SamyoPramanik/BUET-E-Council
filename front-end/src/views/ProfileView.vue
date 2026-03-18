<template>
  <div class="min-h-screen bg-gray-50 pb-12">
    <div class="h-6 mb-4"></div>

    <div class="mx-auto w-full lg:w-3/5 px-4 sm:px-6">
      
      <div class="bg-white rounded-[2rem] shadow-sm border border-gray-100 p-6 sm:p-8 mb-8 flex items-center gap-6">
        <div class="h-20 w-20 bg-blue-600 rounded-2xl flex items-center justify-center text-white text-3xl font-black shadow-xl shadow-blue-200 uppercase">
          {{ userInitials }}
        </div>
        <div>
          <h1 class="text-2xl font-black text-slate-800 tracking-tight">{{ userEmail }}</h1>
          <div class="flex gap-2 mt-2">
            <span 
              class="px-3 py-1 text-[10px] font-black uppercase rounded-lg tracking-widest border"
              :class="userRole === 'admin' ? 'bg-blue-50 text-blue-700 border-blue-100' : 'bg-slate-50 text-slate-600 border-slate-100'"
            >
              {{ userRole }}
            </span>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-[2rem] shadow-xl shadow-slate-200/40 border border-gray-100 overflow-hidden">
        <div class="p-8 border-b border-gray-50 flex justify-between items-center">
          <div>
            <h2 class="text-xl font-black text-slate-800">Security & Sessions</h2>
            <p class="text-sm text-slate-500 font-medium">Manage devices where you are currently signed in</p>
          </div>
          <button 
            @click="fetchProfileData" 
            :disabled="isLoading"
            class="p-3 hover:bg-slate-50 rounded-2xl transition-all border border-transparent hover:border-slate-100 group"
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              class="h-6 w-6 text-slate-400 group-hover:text-blue-600 transition-colors" 
              :class="{ 'animate-spin': isLoading }"
              fill="none" viewBox="0 0 24 24" stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead class="bg-slate-50/50 text-slate-400 text-[10px] uppercase font-black tracking-[0.2em]">
              <tr>
                <th class="px-8 py-4">Device / Identity</th>
                <th class="px-8 py-4">Logged In At</th>
                <th class="px-8 py-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50">
              <tr v-for="session in sessions" :key="session.id" 
                  :class="session.is_current ? 'bg-blue-50/30' : 'hover:bg-slate-50/30 transition-colors'">
                <td class="px-8 py-6">
                  <div class="flex flex-col">
                    <span class="text-sm font-bold text-slate-700 flex items-center gap-3">
                      {{ parseUserAgent(session.user_agent) }}
                      <span v-if="session.is_current" class="text-[9px] bg-blue-600 text-white px-2 py-0.5 rounded-full font-black tracking-tighter uppercase">Active Now</span>
                    </span>
                    <span class="text-xs text-slate-400 font-mono mt-1">{{ session.ip_address }}</span>
                  </div>
                </td>
                <td class="px-8 py-6 text-sm font-medium text-slate-500">
                  {{ formatDate(session.created_at) }}
                </td>
                <td class="px-8 py-6 text-right">
                  <button 
                    @click="handleRevoke(session.id, session.is_current)"
                    class="px-4 py-2 rounded-xl font-black text-xs uppercase transition-all border shadow-sm active:scale-95"
                    :class="session.is_current 
                        ? 'text-red-600 bg-red-50 border-red-100 hover:bg-red-100' 
                        : 'text-slate-600 bg-white border-slate-200 hover:bg-slate-50 hover:text-red-600 hover:border-red-200'"
                    >
                    {{ session.is_current ? 'End Session' : 'Revoke' }}
                    </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="p-8 bg-slate-50/50 flex justify-center sm:justify-end border-t border-slate-100">
          <button 
            @click="handleRevokeAll"
            class="w-full sm:w-auto px-8 py-4 bg-white border-2 border-red-100 text-red-600 rounded-2xl text-xs font-black hover:bg-red-600 hover:text-white hover:border-red-600 transition-all shadow-sm uppercase tracking-widest active:scale-95"
          >
            Sign out from all devices
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import { authState } from '../store/auth'; // Reactive store
import api from '../utils/api';
import { confirmDestructive } from '../utils/alerts';

const router = useRouter();
const toast = useToast();

const sessions = ref([]);
const isLoading = ref(false);

// Reactive data from store
const userEmail = computed(() => authState.userEmail);
const userRole = computed(() => authState.userRole);
const userInitials = computed(() => (userEmail.value || '??').substring(0, 2));

const fetchProfileData = async () => {
  isLoading.value = true;
  try {
    const response = await api.get('/users/me');
    // We update the local sessions list
    sessions.value = response.data.sessions;
    // We also sync the store just in case role changed on backend
    authState.userRole = response.data.user_info.role;
    authState.userEmail = response.data.user_info.email;
  } catch (error) {
    toast.error("Failed to load profile data.");
  } finally {
    isLoading.value = false;
  }
};

const handleRevoke = async (targetId, isSelf) => {
  const isConfirmed = await confirmDestructive(
    isSelf ? 'Sign Out?' : 'Revoke Session?',
    isSelf ? 'You will be redirected to the sign-in page.' : 'This device will be disconnected immediately.',
    isSelf ? 'Sign Out' : 'Revoke'
  );

  if (!isConfirmed) return;

  try {
    await api.delete(`/users/sessions/${targetId}`);
    if (isSelf) {
      toast.success("Signed out successfully");
      authState.clear(); // This triggers the Navbar and Router instantly
      router.push('/sign-in');
    } else {
      toast.success("Session revoked");
      await fetchProfileData();
    }
  } catch (error) {
    toast.error("Action failed.");
  }
};

const handleRevokeAll = async () => {
  const isConfirmed = await confirmDestructive(
    'Sign out all devices?',
    'This will end all sessions including this one. You will need to log back in.',
    'Sign Out All'
  );

  if (!isConfirmed) return;

  try {
    await api.delete('/users/sessions');
    toast.success("All devices signed out");
    authState.clear(); // Dynamic update
    router.push('/sign-in');
  } catch (error) {
    toast.error("Failed to clear sessions.");
  }
};

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('en-GB', {
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
  });
};

const parseUserAgent = (ua) => {
  if (ua.includes('Mobi')) return 'Mobile Device';
  if (ua.includes('Windows')) return 'Windows PC';
  if (ua.includes('Linux')) return 'Linux Desktop';
  if (ua.includes('Macintosh')) return 'MacBook / iMac';
  return 'Unknown Device';
};

onMounted(() => {
  fetchProfileData();
});
</script>