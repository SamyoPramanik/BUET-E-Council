import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import { useAuth } from '../auth/AuthContext'

export default function Navbar() {
  const navigate = useNavigate()
  const { isAuthenticated, userEmail, userRole, clear } = useAuth()

  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const userInitials = (userEmail || '??').substring(0, 2).toUpperCase()

  const goToAdmin = () => {
    window.open('/admin/', '_blank', 'noopener,noreferrer')
  }

  const handleLogout = () => {
    clear()
    setIsDropdownOpen(false)
    toast.info('Logged out successfully')
    navigate('/sign-in')
  }

  // Handle closing when clicking outside the profile menu.
  // (This manual listener is the one working click-outside pattern in the
  // Vue app — the `v-click-outside` directive used elsewhere was never
  // registered and is a no-op; see AUTH_MIGRATION.md / MIGRATION_PLAN.md.)
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false)
      }
    }
    window.addEventListener('click', handleClickOutside)
    return () => window.removeEventListener('click', handleClickOutside)
  }, [])

  return (
    <nav className="w-full py-4 px-8 flex items-center justify-between bg-white border-b border-gray-100 shadow-sm sticky top-0 z-50">
      <Link
        to="/"
        className="text-2xl font-black tracking-tighter text-blue-600 hover:text-blue-700 transition-all active:scale-95"
      >
        BUET_Ecouncil
      </Link>

      {isAuthenticated && (
        <div className="flex items-center gap-4">
          {userRole === 'admin' && (
            <button
              onClick={goToAdmin}
              className="hidden sm:flex items-center gap-2 px-4 py-2 text-sm font-bold text-gray-700 hover:bg-gray-100 rounded-xl transition-colors border border-gray-200"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Admin Panel
            </button>
          )}

          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setIsDropdownOpen((v) => !v)}
              className="w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-sm uppercase shadow-md hover:bg-blue-700 transition-transform active:scale-90"
            >
              {userInitials}
            </button>

            {isDropdownOpen && (
              <div className="absolute right-0 mt-3 w-64 bg-white rounded-2xl shadow-2xl border border-gray-100 py-2 z-[60]">
                <div className="px-4 py-3 border-b border-gray-50 mb-2">
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-[10px] text-gray-400 font-black uppercase tracking-widest">Account</p>
                    <span
                      className={[
                        'px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-tighter',
                        userRole === 'admin' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600',
                      ].join(' ')}
                    >
                      {userRole}
                    </span>
                  </div>
                  <p className="text-sm font-bold text-gray-900 truncate">{userEmail}</p>
                </div>

                <Link
                  to="/profile"
                  className="flex items-center gap-3 px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors"
                  onClick={() => setIsDropdownOpen(false)}
                >
                  Profile Settings
                </Link>

                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-sm font-medium text-red-600 hover:bg-red-50 transition-colors text-left"
                >
                  Sign out
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </nav>
  )
}
