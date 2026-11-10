import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { SearchField } from './search-field'

describe('SearchField', () => {
  it('can show an aligned visible label above its full-width input', () => {
    render(
      <div className="grid grid-cols-3">
        <SearchField label="Search inquiries" placeholder="Search name or code" showLabel />
      </div>,
    )

    const input = screen.getByRole('textbox', { name: 'Search inquiries' })
    expect(input).toHaveClass('h-10', 'w-full')
    expect(screen.getByText('Search inquiries')).toBeVisible()
  })
})
