<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { confirmDestructive } from '../utils/alerts'
import api from '../utils/api'

const toast = useToast()

const users = ref([])
const isLoading = ref(false)

// Create user modal
const showModal = ref(false)
const createEmail = ref('')
const createRole = ref('viewer')
const createPassword = ref('')
const autoGenerate = ref(true)
const isCreating = ref(false)
const generatedPassword = ref(null)
const copied = ref(false)

const fetchUsers = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/users/')
    users.value = res.data
  } catch {
    toast.error("Failed to load users.")
  } finally {
    isLoading.value = false
  }
}

const openModal = () => {
  createEmail.value = ''
  createRole.value = 'viewer'
  createPassword.value = ''
  autoGenerate.value = true
  generatedPassword.value = null
  copied.value = false
  showModal.value = true
}

const handleCreate = async () => {
  if (!createEmail.value) {
    toast.error("Email is required.")
    return
  }
  isCreating.value = true
  try {
    const body = {
      email: createEmail.value,
      role: createRole.value,
      password: autoGenerate.value ? null : createPassword.value || null,
    }
    const res = await api.post('/users/', body)
    if (res.data.generated_password) {
      generatedPassword.value = res.data.generated_password
    } else {
      toast.success("User created.")
      showModal.value = false
    }
    await fetchUsers()
  } catch (error) {
    toast.error(error.response?.data?.detail || "Failed to create user.")
  } finally {
    isCreating.value = false
  }
}

const copyPassword = async () => {
  try {
    await navigator.clipboard.writeText(generatedPassword.value)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    toast.error("Could not copy.")
  }
}

const handleResetPassword = async (userId) => {
  const confirmed = await confirmDestructive(
    "Reset password?",
    "A new password will be auto-generated. You will need to share it with the user.",
    "Reset"
  )
  if (!confirmed) return
  try {
    const res = await api.patch(`/users/${userId}`, { password: null })
    if (res.data.generated_password) {
      await navigator.clipboard.writeText(res.data.generated_password).catch(() => null)
      toast.success(`New password: ${res.data.generated_password} (copied to clipboard)`, { timeout: 10000 })
    }
  } catch {
    toast.error("Failed to reset password.")
  }
}

const handleChangeRole = async (userId, newRole) => {
  try {
    await api.patch(`/users/${userId}`, { role: newRole })
    toast.success("Role updated.")
    await fetchUsers()
  } catch {
    toast.error("Failed to update role.")
  }
}

const handleDelete = async (userId, email) => {
  const confirmed = await confirmDestructive(
    `Delete ${email}?`,
    "This action cannot be undone.",
    "Delete"
  )
  if (!confirmed) return
  try {
    await api.delete(`/users/${userId}`)
    toast.success("User deleted.")
    await fetchUsers()
  } catch {
    toast.error("Failed to delete user.")
  }
}

const formatDate = (d) => new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })

const roleBadge = (role) => ({
  admin: 'bg-blue-50 text-blue-700 border-blue-100',
  staff: 'bg-green-50 text-green-700 border-green-100',
  viewer: 'bg-slate-50 text-slate-500 border-slate-100',
}[role] || 'bg-slate-50 text-slate-500 border-slate-100')

onMounted(fetchUsers)
</script>

<template>
  <div class="min-h-screen bg-gray-50 pb-12">
    <div class="h-6 mb-4"></div>
    <div class="mx-auto w-full lg:w-4/5 px-4 sm:px-6">

      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-2xl font-black text-slate-800">User Management</h1>
          <p class="text-slate-500 text-sm mt-1">Create and manage system accounts</p>
        </div>
        <button
          @click="openModal"
          class="flex items-center gap-2 bg-blue-600 text-white px-5 py-3 rounded-2xl font-bold hover:bg-blue-700 transition-all shadow-lg shadow-blue-200 text-sm"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 4v16m8-8H4"/></svg>
          Add User
        </button>
      </div>

      <div class="bg-white rounded-[2rem] shadow-sm border border-gray-100 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left">
            <thead class="bg-slate-50/50 text-slate-400 text-[10px] uppercase font-black tracking-[0.2em]">
              <tr>
                <th class="px-8 py-4">Email</th>
                <th class="px-8 py-4">Role</th>
                <th class="px-8 py-4">Created</th>
                <th class="px-8 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50">
              <tr v-if="isLoading">
                <td colspan="4" class="px-8 py-10 text-center text-slate-400 text-sm">Loading…</td>
              </tr>
              <tr v-else-if="users.length === 0">
                <td colspan="4" class="px-8 py-10 text-center text-slate-400 text-sm">No users found.</td>
              </tr>
              <tr v-for="user in users" :key="user.id" class="hover:bg-slate-50/30 transition-colors">
                <td class="px-8 py-5 text-sm font-semibold text-slate-700">{{ user.email }}</td>
                <td class="px-8 py-5">
                  <select
                    :value="user.role"
                    @change="handleChangeRole(user.id, $event.target.value)"
                    class="text-[10px] font-black uppercase tracking-wider border rounded-lg px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
                    :class="roleBadge(user.role)"
                  >
                    <option value="viewer">Viewer</option>
                    <option value="staff">Staff</option>
                    <option value="admin">Admin</option>
                  </select>
                </td>
                <td class="px-8 py-5 text-sm text-slate-400 font-medium">{{ formatDate(user.created_at) }}</td>
                <td class="px-8 py-5">
                  <div class="flex items-center justify-end gap-2">
                    <button
                      @click="handleResetPassword(user.id)"
                      class="px-3 py-2 text-xs font-bold text-slate-600 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 hover:border-blue-200 hover:text-blue-600 transition-all"
                    >
                      Reset PW
                    </button>
                    <button
                      @click="handleDelete(user.id, user.email)"
                      class="px-3 py-2 text-xs font-bold text-red-600 bg-red-50 border border-red-100 rounded-xl hover:bg-red-100 transition-all"
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create User Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm px-4">
        <div class="bg-white rounded-[2rem] shadow-2xl w-full max-w-md p-8">
          <h2 class="text-xl font-black text-slate-800 mb-6">Create User</h2>

          <div v-if="!generatedPassword" class="flex flex-col gap-4">
            <!-- Email -->
            <div class="relative">
              <input v-model="createEmail" type="email" placeholder=" " id="cu-email"
                class="block w-full px-4 py-4 text-slate-900 bg-transparent border-2 border-slate-200 rounded-2xl appearance-none focus:outline-none focus:border-blue-500 peer transition-all"
              />
              <label for="cu-email" class="absolute text-slate-400 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-white px-2 peer-focus:text-blue-500 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:scale-75 peer-focus:-translate-y-4 left-3 pointer-events-none font-bold">
                Email Address
              </label>
            </div>

            <!-- Role -->
            <div>
              <label class="block text-xs font-bold text-slate-500 mb-2 uppercase tracking-wider">Role</label>
              <div class="flex gap-2">
                <button v-for="r in ['viewer', 'staff', 'admin']" :key="r"
                  @click="createRole = r"
                  class="flex-1 py-2 rounded-xl text-xs font-black uppercase tracking-wider border transition-all"
                  :class="createRole === r ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-slate-500 border-slate-200 hover:border-blue-200'"
                >
                  {{ r }}
                </button>
              </div>
            </div>

            <!-- Password option -->
            <div>
              <label class="block text-xs font-bold text-slate-500 mb-2 uppercase tracking-wider">Password</label>
              <div class="flex gap-2 mb-3">
                <button @click="autoGenerate = true"
                  class="flex-1 py-2 rounded-xl text-xs font-black uppercase tracking-wider border transition-all"
                  :class="autoGenerate ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-slate-500 border-slate-200'"
                >
                  Auto-generate
                </button>
                <button @click="autoGenerate = false"
                  class="flex-1 py-2 rounded-xl text-xs font-black uppercase tracking-wider border transition-all"
                  :class="!autoGenerate ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-slate-500 border-slate-200'"
                >
                  Set manually
                </button>
              </div>
              <input v-if="!autoGenerate"
                v-model="createPassword"
                type="text"
                placeholder="Enter password"
                class="w-full px-4 py-3 border-2 border-slate-200 rounded-2xl text-sm focus:outline-none focus:border-blue-500"
              />
            </div>

            <div class="flex gap-3 mt-2">
              <button @click="showModal = false"
                class="flex-1 py-3 rounded-2xl font-bold text-slate-600 border border-slate-200 hover:bg-slate-50 transition-all text-sm"
              >
                Cancel
              </button>
              <button @click="handleCreate" :disabled="isCreating"
                class="flex-1 py-3 rounded-2xl font-bold bg-blue-600 text-white hover:bg-blue-700 disabled:bg-blue-300 transition-all text-sm flex items-center justify-center gap-2"
              >
                <svg v-if="isCreating" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                </svg>
                Create
              </button>
            </div>
          </div>

          <!-- Show generated password -->
          <div v-else class="text-center">
            <div class="text-green-500 text-4xl mb-4">✓</div>
            <p class="font-bold text-slate-700 mb-2">User created!</p>
            <p class="text-sm text-slate-500 mb-4">Share this password with the user. It won't be shown again.</p>
            <div class="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 mb-6">
              <span class="flex-1 font-mono text-slate-800 font-bold tracking-widest text-sm">{{ generatedPassword }}</span>
              <button @click="copyPassword"
                class="p-2 rounded-xl hover:bg-white transition-all border border-transparent hover:border-slate-200"
                :title="copied ? 'Copied!' : 'Copy'"
              >
                <svg v-if="!copied" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
              </button>
            </div>
            <button @click="showModal = false"
              class="w-full py-3 rounded-2xl font-bold bg-blue-600 text-white hover:bg-blue-700 transition-all text-sm"
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
