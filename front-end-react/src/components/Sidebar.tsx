import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { Users as UsersIcon, GraduationCap, LibraryBig } from 'lucide-react'
import { useAuth } from '../auth/AuthContext'
import './Sidebar.css'

export default function Sidebar() {
  const { isAuthenticated, userRole } = useAuth()
  const [isExpanded, setIsExpanded] = useState(false)

  if (!isAuthenticated) return null

  return (
    <aside className={['sidebar-container', isExpanded ? 'is-expanded' : ''].join(' ')}>
      <button onClick={() => setIsExpanded((v) => !v)} className="menu-toggle">
        <div className={['hamburger', isExpanded ? 'is-active' : ''].join(' ')}>
          <span></span>
          <span></span>
          <span></span>
        </div>
      </button>

      <nav className="nav-links mt-4">
        <NavLink to="/meetings" className={({ isActive }) => ['nav-item', isActive ? 'is-active' : ''].join(' ')}>
          <div className="icon-wrapper">
            <UsersIcon size={20} />
          </div>
          <span className="nav-text">Meetings</span>
        </NavLink>

        <NavLink
          to="/participants"
          className={({ isActive }) => ['nav-item', isActive ? 'nav-item--active' : ''].join(' ')}
        >
          <div className="icon-wrapper">
            <GraduationCap size={20} />
          </div>
          <span className="nav-label">Participants</span>
        </NavLink>

        {userRole === 'admin' && (
          <NavLink to="/directory" className={({ isActive }) => ['nav-item', isActive ? 'is-active' : ''].join(' ')}>
            <div className="icon-wrapper">
              <LibraryBig size={20} />
            </div>
            <span className="nav-text">Directory</span>
          </NavLink>
        )}
      </nav>
    </aside>
  )
}
