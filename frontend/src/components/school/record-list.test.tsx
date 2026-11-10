import { render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { RecordList } from './record-list'

describe('RecordList pagination', () => {
  it('moves back to the last available page when the current page becomes empty', async () => {
    const onPageChange = vi.fn()
    render(
      <RecordList
        columns={[]}
        emptyMessage="No records"
        error={undefined}
        getRowId={(row: { id: number }) => row.id}
        isLoading={false}
        onPageChange={onPageChange}
        onRetry={vi.fn()}
        pagination={{ page: 2, limit: 10, total_records: 3, total_pages: 1 }}
        rows={[]}
      />,
    )

    await waitFor(() => expect(onPageChange).toHaveBeenCalledWith(1))
    expect(screen.getByText('Page 1 of 1')).toBeInTheDocument()
  })
})
