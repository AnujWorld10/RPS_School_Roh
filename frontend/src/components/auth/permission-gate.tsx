import type { PropsWithChildren, ReactNode } from 'react'
import { useAuth } from '@/features/auth/auth-context'
import { hasAnyPermission } from '@/features/auth/permissions'

type PermissionGateProps = PropsWithChildren<{
  anyOf: string[]
  fallback?: ReactNode
}>

export function PermissionGate({ anyOf, children, fallback = null }: PermissionGateProps) {
  const { user } = useAuth()
  return hasAnyPermission(user?.permissions ?? [], anyOf) ? children : fallback
}
