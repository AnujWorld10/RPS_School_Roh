import { AxiosError, AxiosHeaders } from 'axios'
import type { AxiosAdapter, AxiosResponse } from 'axios'
import { afterEach, describe, expect, it } from 'vitest'
import { apiClient, requestData } from './api-client'
import { ApiError, unwrapEnvelope } from './api-error'
import { clearSessionTokens, getSessionSnapshot } from './token-store'

const originalAdapter = apiClient.defaults.adapter

afterEach(() => {
  apiClient.defaults.adapter = originalAdapter
  clearSessionTokens('logout')
})

describe('API client', () => {
  it('converts the backend error envelope into a typed API error', () => {
    try {
      unwrapEnvelope({
        success: false,
        message: 'Validation failed',
        data: null,
        errors: [{ code: 'VALIDATION_ERROR', message: 'Email is required.', field: 'email' }],
        meta: { request_id: 'request-123', timestamp: '2026-11-04T00:00:00Z' },
      })
      throw new Error('Expected the backend error to be raised.')
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError)
      expect(error).toMatchObject({
        message: 'Validation failed',
        code: 'VALIDATION_ERROR',
        requestId: 'request-123',
        errors: [{ field: 'email', message: 'Email is required.' }],
      })
    }
  })

  it('expires the in-memory session when a protected request returns 401 without a refresh token', async () => {
    const adapter: AxiosAdapter = async (config) => {
      const response: AxiosResponse = {
        data: {
          success: false,
          message: 'Token has expired',
          data: null,
          errors: [{ code: 'AUTH_TOKEN_EXPIRED', message: 'Token has expired' }],
        },
        status: 401,
        statusText: 'Unauthorized',
        headers: new AxiosHeaders(),
        config,
      }

      throw new AxiosError(
        'Unauthorized',
        AxiosError.ERR_BAD_REQUEST,
        config,
        undefined,
        response,
      )
    }
    apiClient.defaults.adapter = adapter

    await expect(requestData({ url: '/private', method: 'GET' })).rejects.toMatchObject({
      status: 401,
      code: 'AUTH_TOKEN_EXPIRED',
      message: 'Token has expired',
    })
    expect(getSessionSnapshot()).toMatchObject({ tokens: null, endReason: 'expired' })
  })
})
