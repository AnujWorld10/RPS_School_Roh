import { useSyncExternalStore, type PropsWithChildren } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { ApiError } from '@/lib/api/api-error'
import {
  clearSessionTokens,
  getRefreshToken,
  getServerSessionSnapshot,
  getSessionSnapshot,
  setSessionTokens,
  subscribeToSession,
} from '@/lib/api/token-store'
import { currentUserQueryOptions, useCurrentUserQuery } from './auth-queries'
import { AuthContext, type AuthContextValue } from './auth-context'
import { loginRequest, logoutRequest } from './auth-api'

export function AuthProvider({ children }: PropsWithChildren) {
  const queryClient = useQueryClient()
  const session = useSyncExternalStore(
    subscribeToSession,
    getSessionSnapshot,
    getServerSessionSnapshot,
  )
  const currentUserQuery = useCurrentUserQuery(Boolean(session.tokens?.accessToken))

  const loginMutation = useMutation({
    mutationFn: async (credentials: Parameters<typeof loginRequest>[0]) => {
      const tokens = await loginRequest(credentials)
      setSessionTokens(tokens)
      try {
        return await queryClient.fetchQuery({
          ...currentUserQueryOptions(),
          staleTime: 0,
        })
      } catch (error) {
        clearSessionTokens('authentication-failed')
        queryClient.removeQueries({ queryKey: currentUserQueryOptions().queryKey })
        throw error
      }
    },
  })

  const logoutMutation = useMutation({
    mutationFn: async () => {
      const refreshToken = getRefreshToken()
      if (!refreshToken) {
        throw new ApiError('No refresh token is available to revoke on the server.')
      }

      try {
        await logoutRequest(refreshToken)
      } finally {
        clearSessionTokens('logout')
        queryClient.removeQueries({ queryKey: currentUserQueryOptions().queryKey })
      }
    },
  })

  const isAuthenticated = Boolean(session.tokens?.accessToken && currentUserQuery.data)
  const value: AuthContextValue = {
    user: isAuthenticated ? currentUserQuery.data ?? null : null,
    isAuthenticated,
    isLoading: Boolean(session.tokens?.accessToken && currentUserQuery.isPending),
    isLoggingIn: loginMutation.isPending,
    isLoggingOut: logoutMutation.isPending,
    sessionExpired: session.endReason === 'expired',
    login: async (credentials) => {
      await loginMutation.mutateAsync(credentials)
    },
    logout: async () => {
      await logoutMutation.mutateAsync()
    },
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
