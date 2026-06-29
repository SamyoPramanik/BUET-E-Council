import { createBrowserRouter, Navigate } from 'react-router-dom'
import MainLayout from '../layouts/MainLayout'
import SignInView from '../views/SignInView'
import VerificationView from '../views/VerificationView'
import UnauthorizedView from '../views/UnauthorizedView'
import ProfileView from '../views/ProfileView'
import MeetingsView from '../views/MeetingsView'
import ParticipantsView from '../views/ParticipantsView'
import MeetingDetailsView from '../views/MeetingDetailsView'
import { RequireAuth, GuestOnly, RequireAdmin, RequirePendingEmail, AdminPanelRedirect } from './guards'

/**
 * Port of router/index.js.
 *
 * One deliberate structural fix vs. the literal Vue source: in the Vue
 * router, '/sign-in', '/verify', and '/meetings/:id' were all nested as
 * *array children* of the '/' route (whose component is MainLayout) even
 * though their own `path` strings start with '/' — comments in that file
 * label them "Auth routes (no shell)" / "Full-screen routes (no shell)",
 * but because they are still children of the MainLayout route record,
 * vue-router renders MainLayout's Sidebar+Navbar around them anyway
 * (matched parent route records always render). For MeetingDetailsView in
 * particular — which renders its own full-viewport header and sidebar
 * internally — that produces a visibly broken double-shell. This port
 * follows the documented intent (no shell) by making these three routes
 * siblings of '/' instead of children, which is how the comments describe
 * the behavior and the only arrangement that doesn't double up chrome
 * around MeetingDetailsView. See PAGES_MIGRATION_REPORT.md.
 */
export const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      { index: true, element: <Navigate to="/meetings" replace /> },
      {
        path: 'profile',
        element: (
          <RequireAuth>
            <ProfileView />
          </RequireAuth>
        ),
      },
      {
        path: 'meetings',
        element: (
          <RequireAuth>
            <MeetingsView />
          </RequireAuth>
        ),
      },
      {
        path: 'participants',
        element: (
          <RequireAuth>
            <ParticipantsView />
          </RequireAuth>
        ),
      },
      {
        path: 'admin-panel',
        element: (
          <RequireAuth>
            <RequireAdmin>
              <AdminPanelRedirect />
            </RequireAdmin>
          </RequireAuth>
        ),
      },
    ],
  },
  {
    path: '/sign-in',
    element: (
      <GuestOnly>
        <SignInView />
      </GuestOnly>
    ),
  },
  {
    path: '/verify',
    element: (
      <GuestOnly>
        <RequirePendingEmail>
          <VerificationView />
        </RequirePendingEmail>
      </GuestOnly>
    ),
  },
  {
    path: '/meetings/:id',
    element: (
      <RequireAuth>
        <MeetingDetailsView />
      </RequireAuth>
    ),
  },
  { path: '/unauthorized', element: <UnauthorizedView /> },
])
