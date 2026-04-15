import { useEffect, type ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated, hydrateToken } = useAuth()

  useEffect(() => { hydrateToken() }, [hydrateToken])

  if (!isAuthenticated && !localStorage.getItem('jwt')) {
    return <Navigate to="/login" replace />
  }
  return <>{children}</>
}
