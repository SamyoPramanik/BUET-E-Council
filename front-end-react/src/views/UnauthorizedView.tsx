import { Link } from 'react-router-dom'

export default function UnauthorizedView() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
      <h1 className="text-6xl font-black text-red-600">403</h1>
      <p className="text-xl font-bold text-gray-800 mt-4">Access Denied</p>
      <p className="text-gray-500 mb-8">You don't have permission to view the admin panel.</p>
      <Link to="/profile" className="text-blue-600 font-bold hover:underline">
        Back to Profile
      </Link>
    </div>
  )
}
