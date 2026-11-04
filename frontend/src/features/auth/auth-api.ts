import { requestData } from '@/lib/api/api-client'
import { ApiError } from '@/lib/api/api-error'
import type { SessionTokens } from '@/lib/api/token-store'

export type LoginCredentials = {
  email: string
  password: string
}

export type LoginTokenResponse = {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export type AuthenticatedUser = {
  id: number
  first_name: string
  last_name: string
  email: string
  phone: string | null
  roles: string[]
  permissions: string[] | null
  status: string
}

export async function loginRequest(credentials: LoginCredentials): Promise<SessionTokens> {
  const result = await requestData<LoginTokenResponse>({
    method: 'POST',
    url: '/auth/login',
    data: credentials,
    skipAuthRefresh: true,
  })

  if (
    typeof result.access_token !== 'string'
    || !result.access_token
    || typeof result.refresh_token !== 'string'
    || !result.refresh_token
    || typeof result.token_type !== 'string'
    || result.token_type.toLowerCase() !== 'bearer'
  ) {
    throw new ApiError('The API returned an incomplete bearer-token login response.')
  }

  return { accessToken: result.access_token, refreshToken: result.refresh_token }
}

export function currentUserRequest() {
  return requestData<AuthenticatedUser>({
    method: 'GET',
    url: '/auth/me',
  })
}

export function logoutRequest(refreshToken: string) {
  return requestData<null>({
    method: 'POST',
    url: '/auth/logout',
    data: { refresh_token: refreshToken },
  })
}
