import { createContext, useContext } from 'react'
import type { AuthenticatedUser, LoginCredentials } from './auth-api'

export type AuthContextValue = {
  user: AuthenticatedUser | null
  isAuthenticated: boolean
  isLoading: boolean
  isLoggingIn: boolean
  isLoggingOut: boolean
  sessionExpired: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider.')
  }
  return context
}
