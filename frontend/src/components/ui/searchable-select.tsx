import { Check, ChevronsUpDown } from 'lucide-react'
import { useId, useMemo, useState } from 'react'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'

export type SearchableOption = {
  value: string
  label: string
}

type SearchableSelectProps = {
  label: string
  value: string
  options: SearchableOption[]
  onChange: (value: string) => void
  placeholder?: string
  disabled?: boolean
}

export function SearchableSelect({
  label,
  value,
  options,
  onChange,
  placeholder = 'Search options…',
  disabled = false,
}: SearchableSelectProps) {
  const id = useId()
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const selected = options.find((option) => option.value === value)
  const filteredOptions = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase()
    return normalizedQuery
      ? options.filter((option) => option.label.toLocaleLowerCase().includes(normalizedQuery))
      : options
  }, [options, query])

  function choose(option: SearchableOption) {
    onChange(option.value)
    setQuery('')
    setOpen(false)
  }

  return (
    <div className="relative grid gap-2">
      <label className="text-sm font-medium text-slate-800" htmlFor={id}>
        {label}
      </label>
      <div className="relative">
        <Input
          aria-autocomplete="list"
          aria-controls={`${id}-options`}
          aria-expanded={open}
          autoComplete="off"
          disabled={disabled}
          id={id}
          onBlur={() => {
            window.setTimeout(() => setOpen(false), 120)
          }}
          onChange={(event) => {
            setQuery(event.target.value)
            setOpen(true)
          }}
          onFocus={() => setOpen(true)}
          onKeyDown={(event) => {
            if (event.key === 'Escape') setOpen(false)
            if (event.key === 'ArrowDown' && filteredOptions[0]) {
              event.preventDefault()
              choose(filteredOptions[0])
            }
          }}
          placeholder={selected?.label ?? placeholder}
          role="combobox"
          value={query}
        />
        <ChevronsUpDown
          aria-hidden="true"
          className="pointer-events-none absolute top-1/2 right-3 size-4 -translate-y-1/2 text-slate-400"
        />
      </div>
      {open ? (
        <ul
          className="absolute top-full z-40 mt-1 max-h-56 w-full overflow-y-auto rounded-lg border border-slate-200 bg-white p-1 shadow-lg"
          id={`${id}-options`}
          role="listbox"
        >
          {value ? (
            <li>
              <button
                className="w-full rounded-md px-2 py-2 text-left text-sm text-slate-500 hover:bg-slate-50"
                onMouseDown={(event) => event.preventDefault()}
                onClick={() => {
                  onChange('')
                  setQuery('')
                  setOpen(false)
                }}
                role="option"
                type="button"
              >
                Clear selection
              </button>
            </li>
          ) : null}
          {filteredOptions.map((option) => (
            <li key={option.value}>
              <button
                aria-selected={value === option.value}
                className={cn(
                  'flex w-full items-center justify-between rounded-md px-2 py-2 text-left text-sm hover:bg-slate-50',
                  value === option.value && 'bg-indigo-50 text-indigo-900',
                )}
                onMouseDown={(event) => event.preventDefault()}
                onClick={() => choose(option)}
                role="option"
                type="button"
              >
                <span>{option.label}</span>
                {value === option.value ? <Check aria-hidden="true" className="size-4" /> : null}
              </button>
            </li>
          ))}
          {filteredOptions.length === 0 ? (
            <li className="px-2 py-2 text-sm text-slate-500">No matching options.</li>
          ) : null}
        </ul>
      ) : null}
    </div>
  )
}
