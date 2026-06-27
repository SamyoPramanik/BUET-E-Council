import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import { isValidEmail } from '../utils/validators'
import { useAuth } from '../auth/AuthContext'
import { requestOtp } from '../auth/authApi'

export default function SignInView() {
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()

  // On mount, if already authenticated, redirect to home. Otherwise, ensure
  // we aren't holding onto old 'pending_email'.
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/')
    }
    localStorage.removeItem('pending_email')
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleSignIn = async () => {
    if (isLoading) return

    // 1. Validation
    if (!email) {
      toast.error('Email is required!')
      return
    }
    if (!isValidEmail(email)) {
      toast.warning('Please enter a valid email address.')
      return
    }

    // 2. API call
    setIsLoading(true)
    try {
      await requestOtp(email)
      toast.success('OTP sent to your email!')
      localStorage.setItem('pending_email', email)
      navigate('/verify')
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

        <div className="relative group mb-8">
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
          <span>{isLoading ? 'Sending OTP...' : 'Get Access Code'}</span>
        </button>

        <p className="mt-8 text-center text-xs text-slate-400 font-medium">An OTP will be sent to your institutional email for verification.</p>
      </div>
    </main>
  )
}
