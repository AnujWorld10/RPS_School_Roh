import axios from 'axios'
import type { AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios'
import { ApiError, toApiError, unwrapEnvelope } from './api-error'
import type { ApiEnvelope } from './types'
import {
  clearSessionTokens,
  getAccessToken,
  getRefreshToken,
  setSessionTokens,
} from './token-store'

declare module 'axios' {
  export interface AxiosRequestConfig {
    _authRetried?: boolean
    skipAuthRefresh?: boolean
  }
}

type RefreshedTokenResponse = {
  access_token: string
  token_type: string
  expires_in: number
}

const apiBaseUrl = (
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'
).replace(/\/+$/, '')

export const apiClient = axios.create({
  baseURL: apiBaseUrl,
  headers: { Accept: 'application/json' },
})

let refreshInFlight: Promise<void> | null = null

async function refreshAccessToken() {
  const refreshToken = getRefreshToken()
  if (!refreshToken) {
    throw new ApiError('Your session could not be renewed. Please sign in again.', {
      status: 401,
      code: 'AUTH_TOKEN_INVALID',
    })
  }

  const response = await axios.post<ApiEnvelope<RefreshedTokenResponse>>(
    `${apiBaseUrl}/auth/refresh-token`,
    { refresh_token: refreshToken },
    { headers: { Accept: 'application/json' } },
  )
  const data = unwrapEnvelope(response.data)

  if (
    typeof data.access_token !== 'string'
    || !data.access_token
    || typeof data.token_type !== 'string'
    || data.token_type.toLowerCase() !== 'bearer'
  ) {
    throw new ApiError('The API returned an invalid refreshed access token.')
  }

  setSessionTokens({ accessToken: data.access_token, refreshToken })
}

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const accessToken = getAccessToken()
  if (accessToken) {
    config.headers.set('Authorization', `Bearer ${accessToken}`)
  }
  return config
})

apiClient.interceptors.response.use(undefined, async (error: unknown) => {
  if (!axios.isAxiosError(error)) {
    throw error
  }

  const config = error.config
  const isAuthEndpoint = config?.url?.includes('/auth/login')
    || config?.url?.includes('/auth/refresh-token')
  if (
    error.response?.status !== 401
    || !config
    || config._authRetried
    || config.skipAuthRefresh
    || isAuthEndpoint
  ) {
    throw error
  }

  if (!getRefreshToken()) {
    clearSessionTokens('expired')
    throw error
  }

  config._authRetried = true
  try {
    refreshInFlight ??= refreshAccessToken().finally(() => {
      refreshInFlight = null
    })
    await refreshInFlight

    const accessToken = getAccessToken()
    if (!accessToken) {
      throw new ApiError('Your session could not be renewed. Please sign in again.', {
        status: 401,
        code: 'AUTH_TOKEN_INVALID',
      })
    }

    config.headers.set('Authorization', `Bearer ${accessToken}`)
    return await apiClient(config)
  } catch (refreshError) {
    clearSessionTokens('expired')
    throw toApiError(refreshError)
  }
})

export async function requestData<T>(config: AxiosRequestConfig): Promise<T> {
  try {
    const response = await apiClient.request<ApiEnvelope<T>>(config)
    return unwrapEnvelope(response.data)
  } catch (error) {
    throw toApiError(error)
  }
}
