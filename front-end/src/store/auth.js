// src/store/auth.js
import { reactive } from 'vue';

export const authState = reactive({
  isAuthenticated: !!localStorage.getItem('session_id'),
  userEmail: localStorage.getItem('user_email') || '',
  userRole: localStorage.getItem('user_role') || '',

  // Call this after login/verify
  refresh() {
    this.isAuthenticated = !!localStorage.getItem('session_id');
    this.userEmail = localStorage.getItem('user_email') || '';
    this.userRole = localStorage.getItem('user_role') || '';
  },

  // Call this on logout
  clear() {
    localStorage.clear();
    document.cookie = "session_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    this.refresh();
  }
});