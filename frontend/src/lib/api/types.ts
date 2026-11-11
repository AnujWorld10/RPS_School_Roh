export type ApiFieldError = {
  code: string
  message: string
  field?: string
}

export type ApiMetadata = {
  request_id: string
  timestamp: string
}

export type ApiPagination = {
  page: number
  limit: number
  total_records: number
  total_pages: number
}

type ApiEnvelopeCommon = {
  message: string
  errors?: ApiFieldError[]
  meta?: ApiMetadata
  pagination?: ApiPagination
  warnings?: Array<Record<string, string>>
}

export type ApiEnvelope<T> =
  | (ApiEnvelopeCommon & { success: true; data: T })
  | (ApiEnvelopeCommon & {
      success: false
      data: null
    })
