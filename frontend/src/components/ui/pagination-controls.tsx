import { ChevronLeft, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'

type PaginationControlsProps = {
  page: number
  totalPages: number
  totalRecords: number
  pageSize?: number
  onPageChange: (page: number) => void
}

export function PaginationControls({
  page,
  totalPages,
  totalRecords,
  pageSize = 10,
  onPageChange,
}: PaginationControlsProps) {
  const displayedTotalPages = Math.max(totalPages, 1)
  const displayedPage = Math.min(Math.max(page, 1), displayedTotalPages)
  const firstRecord = totalRecords === 0 ? 0 : (displayedPage - 1) * pageSize + 1
  const lastRecord = Math.min(displayedPage * pageSize, totalRecords)

  return (
    <nav
      aria-label="Pagination"
      className="flex flex-col gap-3 border-t border-slate-200 px-4 py-3 sm:flex-row sm:items-center sm:justify-between"
    >
      <p className="text-sm text-slate-500">
        Showing <span className="font-medium text-slate-700">{firstRecord}–{lastRecord}</span> of{' '}
        <span className="font-medium text-slate-700">{totalRecords}</span>
      </p>
      <div className="flex items-center gap-2">
        <Button
          aria-label="Go to previous page"
          disabled={displayedPage <= 1}
          onClick={() => onPageChange(displayedPage - 1)}
          size="sm"
          variant="outline"
        >
          <ChevronLeft aria-hidden="true" />
          Previous
        </Button>
        <span aria-current="page" className="min-w-16 text-center text-sm text-slate-600">
          Page {displayedPage} of {displayedTotalPages}
        </span>
        <Button
          aria-label="Go to next page"
          disabled={displayedPage >= displayedTotalPages || totalPages === 0}
          onClick={() => onPageChange(displayedPage + 1)}
          size="sm"
          variant="outline"
        >
          Next
          <ChevronRight aria-hidden="true" />
        </Button>
      </div>
    </nav>
  )
}
