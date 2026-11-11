import { AxiosError, AxiosHeaders } from 'axios'
import type { AxiosAdapter, AxiosRequestConfig, AxiosResponse } from 'axios'
import { afterEach, describe, expect, it } from 'vitest'
import { admissionsApi } from '@/features/admissions/admissions-api'
import { apiClient, publicApiClient, requestData } from './api-client'
import { ApiError, unwrapEnvelope } from './api-error'
import { clearSessionTokens, getSessionSnapshot, setSessionTokens } from './token-store'

const originalAdapter = apiClient.defaults.adapter
const originalPublicAdapter = publicApiClient.defaults.adapter

afterEach(() => {
  apiClient.defaults.adapter = originalAdapter
  publicApiClient.defaults.adapter = originalPublicAdapter
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
        message: 'Validation failed: email: Email is required.',
        code: 'VALIDATION_ERROR',
        requestId: 'request-123',
        errors: [{ field: 'email', message: 'Email is required.' }],
      })
    }
  })

  it('includes all backend field errors in the shared error message', async () => {
    const adapter: AxiosAdapter = async (config) => {
      const response: AxiosResponse = {
        data: {
          success: false,
          message: 'Validation failed',
          data: null,
          errors: [
            { code: 'VALIDATION_ERROR', field: 'body.email', message: 'Enter a valid email address.' },
            { code: 'VALIDATION_ERROR', field: 'body.parent_mobile', message: 'Must contain at least 5 characters.' },
          ],
        },
        status: 422,
        statusText: 'Unprocessable Entity',
        headers: new AxiosHeaders(),
        config,
      }

      throw new AxiosError('Validation failed', AxiosError.ERR_BAD_REQUEST, config, undefined, response)
    }
    apiClient.defaults.adapter = adapter

    await expect(requestData({ url: '/validation-test', method: 'GET' })).rejects.toMatchObject({
      message: 'Validation failed: email: Enter a valid email address.; parent_mobile: Must contain at least 5 characters.',
    })
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

  it('submits public admission as multipart data without forwarding a staff access token', async () => {
    let requestConfig: AxiosRequestConfig | undefined
    const adapter: AxiosAdapter = async (config) => {
      requestConfig = config
      return {
        data: {
          success: true,
          message: 'Admission submitted',
          data: { admission_code: 'ADM202600010', status: 'submitted' },
        },
        status: 201,
        statusText: 'Created',
        headers: new AxiosHeaders(),
        config,
      }
    }
    publicApiClient.defaults.adapter = adapter
    setSessionTokens({ accessToken: 'staff-access-token', refreshToken: 'staff-refresh-token' })

    await expect(admissionsApi.public.submitAdmission({
      inquiry_code: 'INQ202600010',
      email: 'parent@example.com',
      parent_mobile: '+15555550112',
      class_id: 7,
      academic_year: '2026-2027',
      section: 'A',
      student_aadhaar: '123456789012',
      parent_aadhaar: '987654321098',
      last_school_marks: 450,
      last_school_percentage: 90,
      last_school_id_or_roll_number: 'ROLL-12',
    })).resolves.toEqual({ admission_code: 'ADM202600010', status: 'submitted' })

    expect(requestConfig).toMatchObject({
      method: 'post',
      url: '/public/student/admission',
    })
    expect(requestConfig?.headers).not.toHaveProperty('Authorization')
    expect(requestConfig?.data).toBeInstanceOf(FormData)
    expect(requestConfig?.data.get('inquiry_code')).toBe('INQ202600010')
    expect(requestConfig?.data.get('class_id')).toBe('7')
    expect(requestConfig?.data.get('academic_year')).toBe('2026-2027')
  })
})
