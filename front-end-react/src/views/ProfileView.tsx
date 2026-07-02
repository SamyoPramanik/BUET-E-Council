import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import { useAuth } from '../auth/AuthContext'
import api from '../utils/api'
import { confirmDestructive } from '../utils/alerts'
import BackButton from '../components/BackButton'
import type { MeResponse, SessionInfo } from '../types/api'

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function parseUserAgent(ua: string): string {
  if (ua.includes('Mobi')) return 'Mobile Device'
  if (ua.includes('Windows')) return 'Windows PC'
  if (ua.includes('Linux')) return 'Linux Desktop'
  if (ua.includes('Macintosh')) return 'MacBook / iMac'
  return 'Unknown Device'
}

export default function ProfileView() {
  const navigate = useNavigate()
  const { userEmail, userRole, setUserInfo, clear } = useAuth()

  const [sessions, setSessions] = useState<SessionInfo[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const userInitials = (userEmail || '??').substring(0, 2)

  const fetchProfileData = async () => {
    setIsLoading(true)
    try {
      const response = await api.get<MeResponse>('/users/me')
      setSessions(response.data.sessions)
      // We also sync the store just in case role changed on backend
      setUserInfo({ email: response.data.user_info.email, role: response.data.user_info.role })
    } catch {
      toast.error('Failed to load profile data.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchProfileData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleRevoke = async (targetId: string, isSelf: boolean) => {
    const isConfirmed = await confirmDestructive(
      isSelf ? 'Sign Out?' : 'Revoke Session?',
      isSelf ? 'You will be redirected to the sign-in page.' : 'This device will be disconnected immediately.',
      isSelf ? 'Sign Out' : 'Revoke',
    )
    if (!isConfirmed) return
    try {
      await api.delete(`/users/sessions/${targetId}`)
      if (isSelf) {
        toast.success('Signed out successfully')
        clear() // This triggers the Navbar and Router instantly
        navigate('/sign-in')
      } else {
        toast.success('Session revoked')
        await fetchProfileData()
      }
    } catch {
      toast.error('Action failed.')
    }
  }

  const handleRevokeAll = async () => {
    const isConfirmed = await confirmDestructive(
      'Sign out all devices?',
      'This will end all sessions including this one. You will need to log back in.',
      'Sign Out All',
    )
    if (!isConfirmed) return
    try {
      await api.delete('/users/sessions')
      toast.success('All devices signed out')
      clear() // Dynamic update
      navigate('/sign-in')
    } catch {
      toast.error('Failed to clear sessions.')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-12">
      <div className="h-6 mb-4"></div>

      <div className="mx-auto w-full lg:w-3/5 px-4 sm:px-6">
        <BackButton className="mb-3" />
        <div className="bg-white rounded-[2rem] shadow-sm border border-gray-100 p-6 sm:p-8 mb-8 flex items-center gap-6">
          <div className="h-20 w-20 bg-blue-600 rounded-2xl flex items-center justify-center text-white text-3xl font-black shadow-xl shadow-blue-200 uppercase">
            {userInitials}
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-800 tracking-tight">{userEmail}</h1>
            <div className="flex gap-2 mt-2">
              <span
                className={[
                  'px-3 py-1 text-[10px] font-black uppercase rounded-lg tracking-widest border',
                  userRole === 'admin' ? 'bg-blue-50 text-blue-700 border-blue-100' : 'bg-slate-50 text-slate-600 border-slate-100',
                ].join(' ')}
              >
                {userRole}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-[2rem] shadow-xl shadow-slate-200/40 border border-gray-100 overflow-hidden">
          <div className="p-8 border-b border-gray-50 flex justify-between items-center">
            <div>
              <h2 className="text-xl font-black text-slate-800">Security & Sessions</h2>
              <p className="text-sm text-slate-500 font-medium">Manage devices where you are currently signed in</p>
            </div>
            <button onClick={fetchProfileData} disabled={isLoading} className="p-3 hover:bg-slate-50 rounded-2xl transition-all border border-transparent hover:border-slate-100 group">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className={['h-6 w-6 text-slate-400 group-hover:text-blue-600 transition-colors', isLoading ? 'animate-spin' : ''].join(' ')}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead className="bg-slate-50/50 text-slate-400 text-[10px] uppercase font-black tracking-[0.2em]">
                <tr>
                  <th className="px-8 py-4">Device / Identity</th>
                  <th className="px-8 py-4">Logged In At</th>
                  <th className="px-8 py-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {sessions.map((session) => (
                  <tr key={session.id} className={session.is_current ? 'bg-blue-50/30' : 'hover:bg-slate-50/30 transition-colors'}>
                    <td className="px-8 py-6">
                      <div className="flex flex-col">
                        <span className="text-sm font-bold text-slate-700 flex items-center gap-3">
                          {parseUserAgent(session.user_agent)}
                          {session.is_current && (
                            <span className="text-[9px] bg-blue-600 text-white px-2 py-0.5 rounded-full font-black tracking-tighter uppercase">Active Now</span>
                          )}
                        </span>
                        <span className="text-xs text-slate-400 font-mono mt-1">{session.ip_address}</span>
                      </div>
                    </td>
                    <td className="px-8 py-6 text-sm font-medium text-slate-500">{formatDate(session.created_at)}</td>
                    <td className="px-8 py-6 text-right">
                      <button
                        onClick={() => handleRevoke(session.id, session.is_current)}
                        className={[
                          'px-4 py-2 rounded-xl font-black text-xs uppercase transition-all border shadow-sm active:scale-95',
                          session.is_current
                            ? 'text-red-600 bg-red-50 border-red-100 hover:bg-red-100'
                            : 'text-slate-600 bg-white border-slate-200 hover:bg-slate-50 hover:text-red-600 hover:border-red-200',
                        ].join(' ')}
                      >
                        {session.is_current ? 'End Session' : 'Revoke'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="p-8 bg-slate-50/50 flex justify-center sm:justify-end border-t border-slate-100">
            <button
              onClick={handleRevokeAll}
              className="w-full sm:w-auto px-8 py-4 bg-white border-2 border-red-100 text-red-600 rounded-2xl text-xs font-black hover:bg-red-600 hover:text-white hover:border-red-600 transition-all shadow-sm uppercase tracking-widest active:scale-95"
            >
              Sign out from all devices
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
