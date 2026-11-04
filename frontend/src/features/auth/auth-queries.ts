import { useQuery } from '@tanstack/react-query'
import { currentUserRequest } from './auth-api'

export const authQueryKeys = {
  currentUser: ['auth', 'me'] as const,
}

export function currentUserQueryOptions() {
  return {
    queryKey: authQueryKeys.currentUser,
    queryFn: currentUserRequest,
    retry: false,
  }
}

export function useCurrentUserQuery(enabled: boolean) {
  return useQuery({ ...currentUserQueryOptions(), enabled })
}
