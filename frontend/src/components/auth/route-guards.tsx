import type { PropsWithChildren } from 'react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '@/features/auth/auth-context'
import { hasAnyPermission, roleLandingPath } from '@/features/auth/permissions'
import { LoadingState } from '@/components/ui/async-state'
import { ForbiddenPage } from '@/pages/forbidden-page'

export function RequireAuthentication() {
  const auth = useAuth()
  const location = useLocation()

  if (auth.isLoading) {
    return <LoadingState label="Checking your session" />
  }

  if (!auth.isAuthenticated) {
    return (
      <Navigate
        replace
        to="/login"
        state={{ from: location, sessionExpired: auth.sessionExpired }}
      />
    )
  }

  return <Outlet />
}

export function RedirectAuthenticatedUser() {
  const auth = useAuth()
  if (auth.isLoading) {
    return <LoadingState label="Checking your session" />
  }
  return auth.isAuthenticated ? <Navigate replace to={roleLandingPath(auth.user?.roles ?? [])} /> : <Outlet />
}

export function RequireRole({
  anyOf,
  children,
}: PropsWithChildren<{ anyOf: string[] }>) {
  const { user } = useAuth()
  if (!user?.roles.some((role) => anyOf.includes(role))) {
    return <ForbiddenPage />
  }
  return children ?? <Outlet />
}

export function RequirePermission({
  anyOf,
  allOf = [],
  children,
}: PropsWithChildren<{ anyOf?: string[]; allOf?: string[] }>) {
  const { user } = useAuth()
  const permissions = user?.permissions ?? []
  if (!hasAnyPermission(permissions, anyOf ?? []) || !allOf.every((permission) => permissions.includes(permission))) {
    return <ForbiddenPage />
  }
  return children
}
