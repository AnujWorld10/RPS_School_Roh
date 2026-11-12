import { useId, useMemo, useState } from 'react'
import type { SchoolClass } from '@/features/school/school-api'

export type ClassSelection = {
  grade: string
  section: string
  academicYear: string
}

type ClassRecordSelectorProps = {
  classes: SchoolClass[]
  initialClassId?: number
  onChange: (selection: ClassSelection, schoolClass: SchoolClass | null) => void
  disabled?: boolean
  labelPrefix?: string
  gradeLabel?: string
  className?: string
}

const noSectionValue = '__no_section__'
const emptySelection: ClassSelection = { grade: '', section: '', academicYear: '' }

function selectionFor(schoolClass: SchoolClass): ClassSelection {
  return {
    grade: schoolClass.name,
    section: schoolClass.section ?? noSectionValue,
    academicYear: schoolClass.academic_year,
  }
}

export function ClassRecordSelector({
  classes,
  initialClassId,
  onChange,
  disabled = false,
  labelPrefix,
  gradeLabel,
  className = '',
}: ClassRecordSelectorProps) {
  const id = useId()
  const [selection, setSelection] = useState<ClassSelection | null>(null)
  const initialClass = classes.find((item) => item.id === initialClassId)
  const currentSelection = useMemo(
    () => selection ?? (initialClass ? selectionFor(initialClass) : emptySelection),
    [initialClass, selection],
  )

  const grades = useMemo(
    () => [...new Set(classes.map((item) => item.name))].sort((left, right) => left.localeCompare(right)),
    [classes],
  )
  const sections = useMemo(() => {
    const values = classes
      .filter((item) => !currentSelection.grade || item.name === currentSelection.grade)
      .map((item) => item.section ?? noSectionValue)
    return [...new Set(values)].sort((left, right) => {
      if (left === noSectionValue) return -1
      if (right === noSectionValue) return 1
      return left.localeCompare(right)
    })
  }, [classes, currentSelection.grade])
  const academicYears = useMemo(
    () => [...new Set(classes
      .filter((item) => (!currentSelection.grade || item.name === currentSelection.grade)
        && (!currentSelection.section || (item.section ?? noSectionValue) === currentSelection.section))
      .map((item) => item.academic_year))].sort((left, right) => right.localeCompare(left)),
    [classes, currentSelection.grade, currentSelection.section],
  )

  function updateSelection(next: ClassSelection) {
    setSelection(next)
    const schoolClass = classes.find((item) => (
      item.name === next.grade
      && (item.section ?? noSectionValue) === next.section
      && item.academic_year === next.academicYear
    )) ?? null
    onChange(next, schoolClass)
  }

  const resolvedGradeLabel = gradeLabel ?? (labelPrefix ? `${labelPrefix} grade` : 'Grade')
  const sectionLabel = labelPrefix ? `${labelPrefix} section` : 'Section'
  const yearLabel = labelPrefix ? `${labelPrefix} academic year` : 'Academic year'
  const selectClassName = 'h-10 w-full min-w-0 rounded-lg border border-input bg-white px-3 text-sm'

  return (
    <div className={`grid gap-3 sm:grid-cols-3 ${className}`.trim()}>
      <label className="grid min-w-0 gap-2 text-sm font-medium" htmlFor={`${id}-grade`}>
        {resolvedGradeLabel}
        <select
          className={selectClassName}
          disabled={disabled}
          id={`${id}-grade`}
          onChange={(event) => updateSelection({
            grade: event.target.value,
            section: '',
            academicYear: '',
          })}
          value={currentSelection.grade}
        >
          <option value="">Select a grade</option>
          {grades.map((grade) => <option key={grade} value={grade}>{grade}</option>)}
        </select>
      </label>
      <label className="grid min-w-0 gap-2 text-sm font-medium" htmlFor={`${id}-section`}>
        {sectionLabel}
        <select
          className={selectClassName}
          disabled={disabled || !currentSelection.grade}
          id={`${id}-section`}
          onChange={(event) => updateSelection({
            ...currentSelection,
            section: event.target.value,
            academicYear: '',
          })}
          value={currentSelection.section}
        >
          <option value="">Select a section</option>
          {sections.map((section) => (
            <option key={section} value={section}>
              {section === noSectionValue ? 'No section' : section}
            </option>
          ))}
        </select>
      </label>
      <label className="grid min-w-0 gap-2 text-sm font-medium" htmlFor={`${id}-year`}>
        {yearLabel}
        <select
          className={selectClassName}
          disabled={disabled || !currentSelection.grade || !currentSelection.section}
          id={`${id}-year`}
          onChange={(event) => updateSelection({ ...currentSelection, academicYear: event.target.value })}
          value={currentSelection.academicYear}
        >
          <option value="">Select an academic year</option>
          {academicYears.map((year) => <option key={year} value={year}>{year}</option>)}
        </select>
      </label>
    </div>
  )
}
