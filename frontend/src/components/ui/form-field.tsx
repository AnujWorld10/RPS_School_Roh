import type { ReactNode } from 'react'
import { useId } from 'react'

type FormFieldProps = {
  label: string
  description?: string
  error?: string
  required?: boolean
  children: (props: { id: string; describedBy?: string }) => ReactNode
}

export function FormField({
  label,
  description,
  error,
  required = false,
  children,
}: FormFieldProps) {
  const id = useId()
  const descriptionId = description ? `${id}-description` : undefined
  const errorId = error ? `${id}-error` : undefined
  const describedBy = [descriptionId, errorId].filter(Boolean).join(' ') || undefined

  return (
    <div className="grid gap-2">
      <label className="text-sm font-medium text-slate-800" htmlFor={id}>
        {label}
        {required ? <span className="ml-1 text-rose-600" aria-label="required">*</span> : null}
      </label>
      {children({ id, describedBy })}
      {description ? (
        <p className="text-xs leading-5 text-slate-500" id={descriptionId}>
          {description}
        </p>
      ) : null}
      {error ? (
        <p className="text-xs font-medium text-rose-700" id={errorId} role="alert">
          {error}
        </p>
      ) : null}
    </div>
  )
}
