import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { SearchableSelect } from './searchable-select'

describe('SearchableSelect', () => {
  it('moves through options with arrow keys and selects only on Enter', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    render(
      <SearchableSelect
        label="Class"
        onChange={onChange}
        options={[
          { value: '1', label: 'Grade 1' },
          { value: '2', label: 'Grade 2' },
        ]}
        value=""
      />,
    )
    const input = screen.getByRole('combobox', { name: 'Class' })

    await user.click(input)
    await user.keyboard('{ArrowDown}')
    const firstOptionId = input.getAttribute('aria-activedescendant')
    expect(firstOptionId).toBeTruthy()
    expect(screen.getByRole('option', { name: 'Grade 1' })).toHaveAttribute('id', firstOptionId)
    expect(onChange).not.toHaveBeenCalled()

    await user.keyboard('{ArrowDown}{Enter}')

    expect(onChange).toHaveBeenCalledWith('2')
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument()
  })

  it('closes on Escape and supports pointer selection without nested interactive options', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    render(
      <SearchableSelect
        label="Class"
        onChange={onChange}
        options={[{ value: '1', label: 'Grade 1' }]}
        value=""
      />,
    )
    const input = screen.getByRole('combobox', { name: 'Class' })
    await user.click(input)
    await user.keyboard('{Escape}')
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument()

    await user.click(input)
    expect(screen.getByRole('option', { name: 'Grade 1' }).querySelector('button')).toBeNull()
    await user.click(screen.getByRole('option', { name: 'Grade 1' }))

    expect(onChange).toHaveBeenCalledWith('1')
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument()
  })
})
