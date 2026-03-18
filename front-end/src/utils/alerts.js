import Swal from 'sweetalert2';

/**
 * A reusable confirmation dialog for destructive actions
 * Styled to match the BUET e-Council design system.
 */
export const confirmDestructive = async (title, text, confirmButtonText = 'Yes, delete it') => {
  const result = await Swal.fire({
    title: title,
    text: text,
    icon: 'warning',
    iconColor: '#ef4444', // Tailwind red-500
    showCancelButton: true,
    confirmButtonText: confirmButtonText,
    cancelButtonText: 'Cancel',
    reverseButtons: true,
    
    // UI Customization
    background: '#ffffff',
    buttonsStyling: false, // Disables default SWAL buttons to use Tailwind classes
    customClass: {
      popup: 'rounded-[2rem] border-none shadow-2xl p-8',
      title: 'text-2xl font-black text-slate-800 pt-4',
      htmlContainer: 'text-slate-500 font-medium pb-2',
      confirmButton: 'bg-red-600 hover:bg-red-700 text-white px-8 py-3 rounded-2xl font-black text-xs uppercase tracking-widest transition-all mx-2 shadow-lg shadow-red-100',
      cancelButton: 'bg-slate-100 hover:bg-slate-200 text-slate-600 px-8 py-3 rounded-2xl font-black text-xs uppercase tracking-widest transition-all mx-2'
    },
    showClass: {
      popup: 'animate__animated animate__fadeInUp animate__faster'
    },
    hideClass: {
      popup: 'animate__animated animate__fadeOutDown animate__faster'
    }
  });
  
  return result.isConfirmed;
};