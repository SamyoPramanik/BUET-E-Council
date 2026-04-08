<template>
  <aside 
    v-if="isAuthenticated"
    class="sidebar-container"
    :class="{ 'is-expanded': isExpanded }"
  >
    <button @click="toggleSidebar" class="menu-toggle">
      <div class="hamburger" :class="{ 'is-active': isExpanded }">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </button>

    <nav class="nav-links mt-4">
      <router-link to="/meetings" class="nav-item" active-class="is-active">
        <div class="icon-wrapper">
          <UsersIcon :size="20" />
        </div>
        <span class="nav-text">Meetings</span>
      </router-link>

            <RouterLink
            to="/participants"
            class="nav-item"
            :class="{ 'nav-item--active': $route.path.startsWith('/participants') }"
          >
            <div class="icon-wrapper">
            <GraduationCap :size="20" />
          </div>
            <span class="nav-label">Participants</span>
      </RouterLink>
    </nav>
  </aside>
</template>

<script setup>
import { ref, computed } from 'vue';
import { authState } from '../store/auth'; // Using your existing auth store

import { Users as UsersIcon, GraduationCap } from 'lucide-vue-next';

const isExpanded = ref(false);
const isAuthenticated = computed(() => authState.isAuthenticated);

const toggleSidebar = () => {
  isExpanded.value = !isExpanded.value;
};
</script>

<style scoped>
/* 1. Sidebar Base Style (Single Column) */
.sidebar-container {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  width: 64px; /* Mini width */
  background: #1e1e2d;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  overflow: hidden;
}

/* 2. Expanded State (Overlaying) */
.sidebar-container.is-expanded {
  width: 240px;
  box-shadow: 4px 0 15px rgba(0, 0, 0, 0.3);
}

/* 3. Hamburger to X Animation */
.menu-toggle {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  cursor: pointer;
}

.hamburger {
  width: 24px;
  height: 18px;
  position: relative;
}

.hamburger span {
  display: block;
  position: absolute;
  height: 2px;
  width: 100%;
  background: #fff;
  transition: 0.25s ease-in-out;
}

.hamburger span:nth-child(1) { top: 0; }
.hamburger span:nth-child(2) { top: 8px; }
.hamburger span:nth-child(3) { top: 16px; }

.hamburger.is-active span:nth-child(1) {
  top: 8px;
  transform: rotate(135deg);
}

.hamburger.is-active span:nth-child(2) {
  opacity: 0;
  left: -60px;
}

.hamburger.is-active span:nth-child(3) {
  top: 8px;
  transform: rotate(-135deg);
}

/* 4. Navigation Links */
.nav-item {
  display: flex;
  align-items: center;
  height: 50px;
  text-decoration: none;
  color: #a2a3b7;
  transition: 0.2s;
}

.nav-item.is-active {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
  border-left: 3px solid #3699ff; /* Active appearance */
}

.icon-wrapper {
  min-width: 64px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: inherit; /* This makes the icon color change with the text */
}

/* Optional: Add a subtle glow to the active icon */
.nav-item.is-active .icon-wrapper {
  filter: drop-shadow(0 0 5px rgba(54, 153, 255, 0.5));
}

.nav-text {
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.2s;
}

.is-expanded .nav-text {
  opacity: 1;
}

/* 5. Hover Effect for Tooltip appearance */
.nav-item:hover .nav-text {
  opacity: 1;
}
</style>