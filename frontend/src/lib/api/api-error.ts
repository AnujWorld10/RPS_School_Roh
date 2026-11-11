import axios from 'axios'
import type { ApiEnvelope, ApiFieldError, ApiMetadata } from './types'

type ErrorEnvelope = {
  message?: string
  errors?: ApiFieldError[]
  meta?: ApiMetadata
}

export class ApiError extends Error {
  readonly status?: number
  readonly code?: string
  readonly errors: ApiFieldError[]
  readonly requestId?: string

  constructor(
    message: string,
    options: {
      status?: number
      code?: string
      errors?: ApiFieldError[]
      requestId?: string
    } = {},
  ) {
    super(message)
    this.name = 'ApiError'
    this.status = options.status
    this.code = options.code
    this.errors = options.errors ?? []
    this.requestId = options.requestId
  }
}

function formatFieldErrors(errors?: ApiFieldError[], baseMessage?: string) {
  const details = errors
    ?.map(({ field, message }) => {
      const fieldName = field?.replace(/^(body|query|path|header)\./, '')
      return fieldName ? `${fieldName}: ${message}` : message
    })
    .filter((detail) => detail !== baseMessage)
    .join('; ')
  return details ? `${baseMessage ?? 'The request failed.'}: ${details}` : baseMessage
}

export function unwrapEnvelope<T>(envelope: ApiEnvelope<T>): T {
  if (!envelope.success) {
    const firstError = envelope.errors?.[0]
    const baseMessage = envelope.message || firstError?.message || 'The request failed.'
    throw new ApiError(formatFieldErrors(envelope.errors, baseMessage) ?? baseMessage, {
      code: firstError?.code,
      errors: envelope.errors,
      requestId: envelope.meta?.request_id,
    })
  }

  return envelope.data
}

export function toApiError(error: unknown): ApiError {
  if (error instanceof ApiError) {
    return error
  }

  if (axios.isAxiosError<ErrorEnvelope>(error)) {
    const body = error.response?.data
    const firstError = body?.errors?.[0]
    const baseMessage = body?.message
      ?? (error.response
        ? `The request failed with status ${error.response.status}.`
        : 'Unable to reach the school management API. Check the API URL and connection.')
    const message = formatFieldErrors(body?.errors, baseMessage) ?? baseMessage

    return new ApiError(message, {
      status: error.response?.status,
      code: firstError?.code,
      errors: body?.errors,
      requestId: body?.meta?.request_id,
    })
  }

  if (error instanceof Error) {
    return new ApiError(error.message)
  }

  return new ApiError('An unexpected error occurred.')
}
