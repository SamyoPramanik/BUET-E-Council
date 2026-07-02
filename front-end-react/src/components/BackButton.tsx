import { ArrowLeft } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

interface BackButtonProps {
  /** Explicit destination. Omit to fall back to browser history (navigate(-1)). */
  to?: string
  label?: string
  className?: string
}

export default function BackButton({ to, label = 'Back', className = '' }: BackButtonProps) {
  const navigate = useNavigate()

  const handleClick = () => {
    if (to) navigate(to)
    else navigate(-1)
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      aria-label={label}
      className={[
        'inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-sm font-semibold',
        'text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-300',
        className,
      ].join(' ')}
    >
      <ArrowLeft size={16} className="shrink-0" />
      {label}
    </button>
  )
}
