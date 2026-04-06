// utils/alerts.js
import Swal from 'sweetalert2'

const baseClass = {
  popup:         'rounded-[2rem] border-none shadow-2xl p-8',
  title:         'text-2xl font-black text-slate-800 pt-4',
  htmlContainer: 'text-slate-500 font-medium pb-2',
}

/**
 * Destructive confirmation (red confirm button).
 * Use for irreversible actions: delete, clear all, discard.
 */
export const confirmDestructive = async (title, text, confirmLabel = 'Yes, Proceed') => {
  const result = await Swal.fire({
    title,
    text,
    icon: 'warning',
    iconColor: '#ef4444',
    showCancelButton: true,
    confirmButtonText: confirmLabel,
    cancelButtonText: 'Cancel',
    reverseButtons: true,
    background: '#ffffff',
    buttonsStyling: false,
    customClass: {
      ...baseClass,
      confirmButton:
        'bg-red-600 hover:bg-red-700 text-white px-8 py-3 rounded-2xl font-black ' +
        'text-xs uppercase tracking-widest transition-all mx-2 shadow-lg shadow-red-100',
      cancelButton:
        'bg-slate-100 hover:bg-slate-200 text-slate-600 px-8 py-3 rounded-2xl font-black ' +
        'text-xs uppercase tracking-widest transition-all mx-2',
    },
  })
  return result.isConfirmed
}

/**
 * Standard confirmation (blue confirm button).
 * Use for save / update actions.
 */
export const confirmAction = async (title, text, confirmLabel = 'Confirm') => {
  const result = await Swal.fire({
    title,
    text,
    icon: 'info',
    iconColor: '#3b82f6',
    showCancelButton: true,
    confirmButtonText: confirmLabel,
    cancelButtonText: 'Cancel',
    reverseButtons: true,
    background: '#ffffff',
    buttonsStyling: false,
    customClass: {
      ...baseClass,
      confirmButton:
        'bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-2xl font-black ' +
        'text-xs uppercase tracking-widest transition-all mx-2 shadow-lg shadow-blue-100',
      cancelButton:
        'bg-slate-100 hover:bg-slate-200 text-slate-600 px-8 py-3 rounded-2xl font-black ' +
        'text-xs uppercase tracking-widest transition-all mx-2',
    },
  })
  return result.isConfirmed
}