<!-- layouts/MainLayout.vue -->
<script setup>
import Navbar from '../components/Navbar.vue'
import Sidebar from '../components/Sidebar.vue'
import { authState } from '../store/auth'
import { computed } from 'vue'

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
.main-content-authenticated {
  margin-left: 64px;
  transition: margin-left 0.3s ease;
  width: calc(100% - 64px);
}
</style>