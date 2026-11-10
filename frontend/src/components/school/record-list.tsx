import { useEffect, type ReactNode } from 'react'
import { ErrorState, LoadingState } from '@/components/ui/async-state'
import { Card, CardContent } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { PaginationControls } from '@/components/ui/pagination-controls'
import type { DataTableColumn } from '@/components/ui/data-table'
import type { ApiPagination } from '@/lib/api/types'

type RecordListProps<T> = {
  rows: T[]
  columns: DataTableColumn<T>[]
  getRowId: (row: T) => string | number
  pagination?: ApiPagination
  onPageChange?: (page: number) => void
  isLoading: boolean
  error?: string
  onRetry: () => void
  emptyMessage: string
  toolbar?: ReactNode
}

export function RecordList<T>({
  rows,
  columns,
  getRowId,
  pagination,
  onPageChange,
  isLoading,
  error,
  onRetry,
  emptyMessage,
  toolbar,
}: RecordListProps<T>) {
  const lastAvailablePage = Math.max(pagination?.total_pages ?? 1, 1)
  const displayedPage = Math.min(pagination?.page ?? 1, lastAvailablePage)

  useEffect(() => {
    if (!pagination || !onPageChange) return
    if (pagination.page > lastAvailablePage) onPageChange(lastAvailablePage)
  }, [lastAvailablePage, onPageChange, pagination])

  if (isLoading) return <LoadingState label="Loading records" />
  if (error) return <ErrorState description={error} onRetry={onRetry} />

  return (
    <Card>
      {toolbar ? <div className="border-b border-slate-200 p-4">{toolbar}</div> : null}
      <CardContent className="overflow-x-auto p-0">
        <DataTable
          caption="School records"
          columns={columns}
          emptyMessage={emptyMessage}
          getRowId={getRowId}
          rows={rows}
        />
      </CardContent>
      {pagination && onPageChange ? (
        <PaginationControls
          onPageChange={onPageChange}
          page={displayedPage}
          pageSize={pagination.limit}
          totalPages={pagination.total_pages}
          totalRecords={pagination.total_records}
        />
      ) : null}
    </Card>
  )
}
