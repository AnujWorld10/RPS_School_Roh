import { apiClient } from './api-client'
import { toApiError, unwrapEnvelope } from './api-error'
import type { ApiEnvelope, ApiPagination } from './types'
import type { AxiosRequestConfig } from 'axios'

export type PaginatedData<T> = {
  items: T[]
  pagination: ApiPagination
}

export async function requestPaginated<T>(
  config: AxiosRequestConfig,
): Promise<PaginatedData<T>> {
  try {
    const response = await apiClient.request<ApiEnvelope<T[]>>(config)
    const items = unwrapEnvelope(response.data)
    if (!response.data.pagination) {
      throw new Error('The API response did not include pagination metadata.')
    }

    return { items, pagination: response.data.pagination }
  } catch (error) {
    throw toApiError(error)
  }
}
