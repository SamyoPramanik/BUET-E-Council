import { createRouter, createWebHistory } from 'vue-router'
import { authState } from '../store/auth'
import { useToast } from 'vue-toastification'
import SignInView from '../views/SignInView.vue'
import VerificationView from '../views/VerificationView.vue'

import MainLayout from '../layouts/MainLayout.vue'

const routes = [
  // ── Auth routes (no shell) ──────────────────────────

  // ── Shell routes (wrapped in MainLayout) ────────────
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        redirect: '/meetings'
      },
      {
        path: 'profile',
        name: 'profile',
        component: () => import('../views/ProfileView.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'meetings',
        name: 'Meetings',
        component: () => import('../views/MeetingsView.vue'),
        meta: { requiresAuth: true }
      },
            {
        path: 'participants',
        name: 'Participants',
        component: () => import('../views/ParticipantsView.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'admin-panel',
        name: 'AdminPanel',
        meta: { requiresAuth: true, requiresAdmin: true },
        beforeEnter: () => {
          window.location.href = 'http://localhost:8000/admin/'
        }
      },
      {
    path: '/sign-in',
    name: 'SignIn',
    component: SignInView,
    meta: { guestOnly: true }
  },
  {
    path: '/verify',
    name: 'Verify',
    component: VerificationView,
    meta: { guestOnly: true },
    beforeEnter: (to, from, next) => {
      const email = localStorage.getItem('pending_email')
      if (!email) next({ name: 'SignIn' }); else next()
    }
  },

  // ── Full-screen routes (no shell) ───────────────────
  {
    path: '/meetings/:id',
    name: 'MeetingDetails',
    component: () => import('../views/MeetingDetailsView.vue'),
    props: true,
    meta: { requiresAuth: true }
  },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const toast = useToast();
  const { isAuthenticated, userRole } = authState;

  // 1. Auth Guard: If page requires auth and user is NOT logged in
  if (to.meta.requiresAuth && !isAuthenticated) {
    toast.error("Please sign in to access this page.");
    return next({ name: 'SignIn' });
  }

  // 2. Guest Guard: If user IS logged in but tries to access login/verify
  if (to.meta.guestOnly && isAuthenticated) {
    return next({ name: 'profile' });
  }

  // 3. Admin Guard
  if (to.meta.requiresAdmin && userRole !== 'admin') {
    toast.error("Access Denied: Admin privileges required.");
    return next({ name: 'profile' }); 
  }

  next(); // Always call next() to finish the hook
})

export default router