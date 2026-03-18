<script setup>
import Navbar from './components/Navbar.vue'
import Sidebar from './components/Sidebar.vue'
import { authState } from './store/auth'
import { computed } from 'vue'

// Only show sidebar and apply layout padding if authenticated
const isAuthenticated = computed(() => authState.isAuthenticated)
</script>

<template>
  <div class="min-h-screen bg-slate-50">
    <Sidebar />

    <div :class="{ 'main-content-authenticated': isAuthenticated }">
      <Navbar />
      
      <main class="p-4">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
/* When authenticated, push the content to the right to make room for the mini-sidebar */
.main-content-authenticated {
  margin-left: 64px;
  transition: margin-left 0.3s ease;
  width: calc(100% - 64px);
}

/* Optional: If you want the sidebar to push content instead of overlaying when expanded, 
   you can add logic here, but standard dashboards usually overlay the expansion. */
</style>