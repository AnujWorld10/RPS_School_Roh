import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import type { SchoolClass } from '@/features/school/school-api'
import { ClassRecordSelector } from './class-record-selector'

const classes: SchoolClass[] = [
  { id: 1, class_teacher_id: null, name: 'Grade 5', section: 'A', academic_year: '2026-2027', capacity: 30, status: 'active' },
  { id: 2, class_teacher_id: null, name: 'Grade 5', section: 'B', academic_year: '2025-2026', capacity: 30, status: 'active' },
  { id: 3, class_teacher_id: null, name: 'Grade 6', section: null, academic_year: '2026-2027', capacity: 30, status: 'active' },
]

describe('ClassRecordSelector', () => {
  it('selects grade, section, and year separately and emits the matching class record', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    render(<ClassRecordSelector classes={classes} onChange={onChange} />)

    const grade = screen.getByRole('combobox', { name: 'Grade' })
    const section = screen.getByRole('combobox', { name: 'Section' })
    const year = screen.getByRole('combobox', { name: 'Academic year' })

    expect(section).toBeDisabled()
    expect(year).toBeDisabled()
    await user.selectOptions(grade, 'Grade 5')
    await user.selectOptions(section, 'B')
    await user.selectOptions(year, '2025-2026')

    expect(onChange).toHaveBeenLastCalledWith(
      { grade: 'Grade 5', section: 'B', academicYear: '2025-2026' },
      classes[1],
    )
  })

  it('supports catalog classes without a section', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()
    render(<ClassRecordSelector classes={classes} onChange={onChange} />)

    await user.selectOptions(screen.getByRole('combobox', { name: 'Grade' }), 'Grade 6')
    await user.selectOptions(screen.getByRole('combobox', { name: 'Section' }), '__no_section__')
    await user.selectOptions(screen.getByRole('combobox', { name: 'Academic year' }), '2026-2027')

    expect(onChange).toHaveBeenLastCalledWith(
      { grade: 'Grade 6', section: '__no_section__', academicYear: '2026-2027' },
      classes[2],
    )
  })
})
