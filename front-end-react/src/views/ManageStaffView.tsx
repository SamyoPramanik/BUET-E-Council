import { useEffect, useState } from 'react'
import { toast } from 'react-toastify'
import api from '../utils/api'
import { isValidEmail } from '../utils/validators'
import { confirmDestructive } from '../utils/alerts'
import { useAuth } from '../auth/AuthContext'
import type { CreateUserRequest, UserAccount } from '../types/api'
import type { UserRole } from '../auth/types'

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

export default function ManageStaffView() {
  const { userEmail: currentUserEmail } = useAuth()

  const [users, setUsers] = useState<UserAccount[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const [email, setEmail] = useState('')
  const [role, setRole] = useState<UserRole>('staff')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  const fetchUsers = async () => {
    setIsLoading(true)
    try {
      const { data } = await api.get<UserAccount[]>('/users')
      setUsers(data)
    } catch {
      toast.error('Failed to load users.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers()
  }, [])

  const handleCreate = async () => {
    if (isSubmitting) return

    if (!email) {
      toast.error('Email is required!')
      return
    }
    if (!isValidEmail(email)) {
      toast.warning('Please enter a valid email address.')
      return
    }

    const payload: CreateUserRequest = { email, role, password: password || undefined }

    setIsSubmitting(true)
    try {
      await api.post('/users', payload)
      toast.success('Account created. Credentials have been emailed.')
      setEmail('')
      setPassword('')
      setRole('staff')
      await fetchUsers()
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Failed to create account.'
      toast.error(errorMsg)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDelete = async (user: UserAccount) => {
    const isConfirmed = await confirmDestructive(
      'Remove this account?',
      `${user.email} will lose access immediately.`,
      'Remove',
    )
    if (!isConfirmed) return
    try {
      await api.delete(`/users/${user.id}`)
      toast.success('Account removed.')
      await fetchUsers()
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Failed to remove account.'
      toast.error(errorMsg)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-12">
      <div className="h-6 mb-4"></div>

      <div className="mx-auto w-full lg:w-3/5 px-4 sm:px-6">
        <div className="bg-white rounded-[2rem] shadow-xl shadow-slate-200/40 border border-gray-100 p-8 mb-8">
          <h2 className="text-xl font-black text-slate-800 mb-1">Add Account</h2>
          <p className="text-sm text-slate-500 font-medium mb-6">
            Create an account and email its login credentials.
          </p>

          <div className="grid sm:grid-cols-3 gap-4 mb-4">
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              type="email"
              placeholder="Email address"
              disabled={isSubmitting}
              className="sm:col-span-2 px-4 py-3 text-slate-900 bg-slate-50 border-2 border-slate-200 rounded-xl focus:outline-none focus:border-blue-500 transition-all disabled:cursor-not-allowed"
            />
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as UserRole)}
              disabled={isSubmitting}
              className="px-4 py-3 text-slate-900 bg-slate-50 border-2 border-slate-200 rounded-xl focus:outline-none focus:border-blue-500 transition-all disabled:cursor-not-allowed"
            >
              <option value="staff">Staff</option>
              <option value="viewer">Viewer</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <div className="relative mb-4">
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type={showPassword ? 'text' : 'password'}
              placeholder="Password (leave blank to auto-generate)"
              disabled={isSubmitting}
              className="w-full px-4 py-3 pr-12 text-slate-900 bg-slate-50 border-2 border-slate-200 rounded-xl focus:outline-none focus:border-blue-500 transition-all disabled:cursor-not-allowed"
            />
            <button
              type="button"
              tabIndex={-1}
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? (
                <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              )}
            </button>
          </div>

          <button
            onClick={handleCreate}
            disabled={isSubmitting}
            className="w-full sm:w-auto px-8 py-3 bg-blue-600 text-white rounded-xl font-black text-xs uppercase tracking-widest hover:bg-blue-700 transition-all active:scale-95 disabled:bg-blue-300 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Creating...' : 'Create Account'}
          </button>
        </div>

        <div className="bg-white rounded-[2rem] shadow-xl shadow-slate-200/40 border border-gray-100 overflow-hidden">
          <div className="p-8 border-b border-gray-50">
            <h2 className="text-xl font-black text-slate-800">All Accounts</h2>
            <p className="text-sm text-slate-500 font-medium">{isLoading ? 'Loading…' : `${users.length} total`}</p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead className="bg-slate-50/50 text-slate-400 text-[10px] uppercase font-black tracking-[0.2em]">
                <tr>
                  <th className="px-8 py-4">Email</th>
                  <th className="px-8 py-4">Role</th>
                  <th className="px-8 py-4">Created</th>
                  <th className="px-8 py-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-slate-50/30 transition-colors">
                    <td className="px-8 py-6 text-sm font-bold text-slate-700">{user.email}</td>
                    <td className="px-8 py-6">
                      <span className="px-3 py-1 text-[10px] font-black uppercase rounded-lg tracking-widest bg-slate-50 text-slate-600 border border-slate-100">
                        {user.role}
                      </span>
                    </td>
                    <td className="px-8 py-6 text-sm font-medium text-slate-500">{formatDate(user.created_at)}</td>
                    <td className="px-8 py-6 text-right">
                      <button
                        onClick={() => handleDelete(user)}
                        disabled={user.email === currentUserEmail}
                        className="px-4 py-2 rounded-xl font-black text-xs uppercase transition-all border shadow-sm active:scale-95 text-slate-600 bg-white border-slate-200 hover:bg-slate-50 hover:text-red-600 hover:border-red-200 disabled:opacity-40 disabled:cursor-not-allowed"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
