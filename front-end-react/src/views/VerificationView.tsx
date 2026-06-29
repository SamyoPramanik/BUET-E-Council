import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import { useAuth } from '../auth/AuthContext'
import { requestOtp, verifyOtp } from '../auth/authApi'

export default function VerificationView() {
  const [otp, setOtp] = useState<string[]>(['', '', '', '', '', ''])
  const [timer, setTimer] = useState(300)
  const [isLoading, setIsLoading] = useState(false)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const inputRefs = useRef<(HTMLInputElement | null)[]>([])

  const navigate = useNavigate()
  const { refresh } = useAuth()

  const isComplete = otp.every((v) => v !== '')

  const formatTime = (() => {
    const mins = Math.floor(timer / 60)
    const secs = timer % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  })()

  // Auto-focus logic
  const handleInput = (e: React.ChangeEvent<HTMLInputElement>, index: number) => {
    const val = e.target.value
    // Ensure only numbers
    if (val && !/^\d+$/.test(val)) {
      setOtp((prev) => prev.map((d, i) => (i === index ? '' : d)))
      return
    }
    setOtp((prev) => prev.map((d, i) => (i === index ? val : d)))
    if (val && index < 5) {
      inputRefs.current[index + 1]?.focus()
    }
  }

  const handleDelete = (e: React.KeyboardEvent<HTMLInputElement>, index: number) => {
    if (e.key !== 'Backspace') return
    if (!otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus()
    }
  }

  const handlePaste = (e: React.ClipboardEvent) => {
    const pasteData = e.clipboardData.getData('text').trim().slice(0, 6).split('')
    if (pasteData.length > 0) {
      setOtp((prev) => {
        const next = [...prev]
        pasteData.forEach((char, index) => {
          if (index < 6 && /^\d$/.test(char)) next[index] = char
        })
        return next
      })
      const nextIndex = Math.min(pasteData.length, 5)
      inputRefs.current[nextIndex]?.focus()
    }
  }

  const startTimer = () => {
    setTimer(300)
    if (intervalRef.current) clearInterval(intervalRef.current)
    intervalRef.current = setInterval(() => {
      setTimer((t) => {
        if (t > 0) return t - 1
        if (intervalRef.current) clearInterval(intervalRef.current)
        return t
      })
    }, 1000)
  }

  const verifyOTP = async () => {
    const code = otp.join('')
    const email = localStorage.getItem('pending_email')

    if (!email) {
      toast.error('Session expired. Please sign in again.')
      navigate('/sign-in')
      return
    }

    setIsLoading(true)
    try {
      const response = await verifyOtp(email, code)

      if (response.status === 'success') {
        const { session_id, user_role } = response.data

        // 1. Save all data to localStorage
        localStorage.setItem('session_id', session_id)
        localStorage.setItem('user_role', user_role)
        localStorage.setItem('user_email', email)

        // 2. Set the cookie for the FastAPI Admin interface
        document.cookie = `session_id=${session_id}; path=/; samesite=lax;`

        // 3. TRIGGER REACTIVE UPDATE
        // This tells the Navbar to show the profile icon immediately
        refresh()

        toast.success('Login successful!')
        localStorage.removeItem('pending_email')

        navigate('/')
      }
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Invalid or expired OTP.'
      toast.error(errorMsg)
      setOtp(['', '', '', '', '', ''])
      inputRefs.current[0]?.focus()
    } finally {
      setIsLoading(false)
    }
  }

  const resendOTP = async () => {
    const email = localStorage.getItem('pending_email')
    if (!email) return
    try {
      await requestOtp(email)
      toast.info('A new code has been sent.')
      startTimer()
    } catch {
      toast.error('Failed to resend OTP.')
    }
  }

  useEffect(() => {
    // If no email is pending, user shouldn't be here
    if (!localStorage.getItem('pending_email')) {
      navigate('/sign-in')
    }
    startTimer()
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="min-h-[85vh] flex flex-col items-center justify-center px-4">
      <div className="max-w-md w-full bg-white p-10 rounded-[2.5rem] shadow-2xl shadow-blue-100/50 border border-slate-100">
        <div className="text-center mb-10">
          <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-3xl font-black text-slate-800">Verification</h2>
          <p className="text-slate-500 mt-2 font-medium">Enter the code sent to your email</p>
        </div>

        <div className="flex justify-center gap-3 mb-10" onPaste={handlePaste}>
          {otp.map((digit, index) => (
            <input
              key={index}
              id={`otp-${index}`}
              ref={(el) => {
                inputRefs.current[index] = el
              }}
              value={digit}
              type="text"
              inputMode="numeric"
              maxLength={1}
              className={[
                'w-12 h-16 text-center text-2xl font-black border-2 rounded-2xl focus:border-blue-600 focus:ring-4 focus:ring-blue-50 outline-none transition-all',
                digit ? 'border-blue-600 bg-white' : 'border-slate-200 bg-slate-50',
              ].join(' ')}
              onChange={(e) => handleInput(e, index)}
              onKeyDown={(e) => handleDelete(e, index)}
            />
          ))}
        </div>

        <button
          onClick={verifyOTP}
          disabled={!isComplete || isLoading}
          className={[
            'w-full py-4 rounded-2xl font-bold transition-all mb-6 flex items-center justify-center gap-2 shadow-lg',
            isComplete && !isLoading ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-blue-200' : 'bg-slate-200 text-slate-400 cursor-not-allowed',
          ].join(' ')}
        >
          {isLoading && (
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth={4} fill="none"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
          )}
          <span>{isLoading ? 'Checking...' : 'Verify & Continue'}</span>
        </button>

        <div className="text-center">
          {timer > 0 ? (
            <p className="text-sm text-slate-400 font-medium">
              Didn't get the code? Wait <span className="font-bold text-blue-600">{formatTime}</span>
            </p>
          ) : (
            <button onClick={resendOTP} className="text-sm font-bold text-blue-600 hover:text-blue-800 transition-colors">
              Resend Access Code
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
