import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import { isValidEmail } from '../utils/validators'
import { useAuth } from '../auth/AuthContext'
import { login } from '../auth/authApi'

export default function SignInView() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()
  const { isAuthenticated, refresh } = useAuth()

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/')
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleSignIn = async () => {
    if (isLoading) return

    // 1. Validation
    if (!email || !password) {
      toast.error('Email and password are required!')
      return
    }
    if (!isValidEmail(email)) {
      toast.warning('Please enter a valid email address.')
      return
    }

    // 2. API call
    setIsLoading(true)
    try {
      const response = await login(email, password)
      const { session_id, user_role } = response.data

      // 3. Save all data to localStorage
      localStorage.setItem('session_id', session_id)
      localStorage.setItem('user_role', user_role)
      localStorage.setItem('user_email', email)

      // 4. Set the cookie for the FastAPI Admin interface
      document.cookie = `session_id=${session_id}; path=/; samesite=lax;`

      // 5. Trigger reactive update so the Navbar shows the profile icon immediately
      refresh()

      toast.success('Login successful!')
      navigate('/')
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Connection to server failed.'
      toast.error(errorMsg)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="flex flex-col items-center justify-center pt-20 px-4 min-h-[80vh]">
      <div className="w-full max-w-md bg-white p-10 rounded-[2rem] shadow-2xl shadow-blue-100/50 border border-slate-100">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-black text-slate-800 mb-2">Welcome Back</h2>
          <p className="text-slate-500 font-medium italic text-sm">BUET e-Council Management</p>
        </div>

        <div className="relative group mb-6">
          <input
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyUp={(e) => e.key === 'Enter' && handleSignIn()}
            type="email"
            id="email"
            placeholder=" "
            disabled={isLoading}
            className="block w-full px-4 py-4 text-slate-900 bg-transparent border-2 border-slate-200 rounded-2xl appearance-none focus:outline-none focus:border-blue-500 peer transition-all disabled:bg-slate-50 disabled:cursor-not-allowed"
          />
          <label
            htmlFor="email"
            className="absolute text-slate-400 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-white px-2 peer-focus:px-2 peer-focus:text-blue-500 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:scale-75 peer-focus:-translate-y-4 left-3 pointer-events-none font-bold"
          >
            Email Address
          </label>
        </div>

        <div className="relative group mb-8">
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyUp={(e) => e.key === 'Enter' && handleSignIn()}
            type={showPassword ? 'text' : 'password'}
            id="password"
            placeholder=" "
            disabled={isLoading}
            className="block w-full px-4 py-4 pr-12 text-slate-900 bg-transparent border-2 border-slate-200 rounded-2xl appearance-none focus:outline-none focus:border-blue-500 peer transition-all disabled:bg-slate-50 disabled:cursor-not-allowed"
          />
          <label
            htmlFor="password"
            className="absolute text-slate-400 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-white px-2 peer-focus:px-2 peer-focus:text-blue-500 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:scale-75 peer-focus:-translate-y-4 left-3 pointer-events-none font-bold"
          >
            Password
          </label>
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
          onClick={handleSignIn}
          disabled={isLoading}
          className="w-full bg-blue-600 text-white py-4 rounded-2xl font-bold hover:bg-blue-700 transition-all active:scale-[0.98] disabled:bg-blue-300 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg shadow-blue-200"
        >
          {isLoading && (
            <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth={4}></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          )}
          <span>{isLoading ? 'Signing in...' : 'Sign In'}</span>
        </button>

        <p className="mt-8 text-center text-xs text-slate-400 font-medium">
          Don't have an account? Contact an administrator to have one created for you.
        </p>
      </div>
    </main>
  )
}
