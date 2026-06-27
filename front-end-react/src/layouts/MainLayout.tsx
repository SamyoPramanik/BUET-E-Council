import { Outlet } from 'react-router-dom'
import Navbar from '../components/Navbar'
import Sidebar from '../components/Sidebar'
import { useAuth } from '../auth/AuthContext'
import './MainLayout.css'

export default function MainLayout() {
  const { isAuthenticated } = useAuth()

  return (
    <div className="min-h-screen bg-slate-50">
      <Sidebar />
      <div className={isAuthenticated ? 'main-content-authenticated' : ''}>
        <Navbar />
        <main className="p-4">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
