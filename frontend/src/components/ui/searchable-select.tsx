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
  const [activeIndex, setActiveIndex] = useState(-1)
  const selected = options.find((option) => option.value === value)
  const filteredOptions = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase()
    return normalizedQuery
      ? options.filter((option) => option.label.toLocaleLowerCase().includes(normalizedQuery))
      : options
  }, [options, query])
  const listboxOptions = useMemo(
    () => [
      ...(value ? [{ value: '', label: 'Clear selection' }] : []),
      ...filteredOptions,
    ],
    [filteredOptions, value],
  )

  function choose(option: SearchableOption) {
    onChange(option.value)
    setQuery('')
    setOpen(false)
    setActiveIndex(-1)
  }

  return (
    <div className="relative grid min-w-0 gap-2">
      <label className="text-sm font-medium text-slate-800" htmlFor={id}>
        {label}
      </label>
      <div className="relative">
        <Input
          className="h-10"
          aria-autocomplete="list"
          aria-controls={`${id}-options`}
          aria-activedescendant={open && activeIndex >= 0 ? `${id}-option-${activeIndex}` : undefined}
          aria-expanded={open}
          autoComplete="off"
          disabled={disabled}
          id={id}
          onBlur={() => setOpen(false)}
          onChange={(event) => {
            setQuery(event.target.value)
            setOpen(true)
            setActiveIndex(0)
          }}
          onClick={() => {
            setOpen(true)
            setActiveIndex(-1)
          }}
          onFocus={() => {
            setOpen(true)
            setActiveIndex(-1)
          }}
          onKeyDown={(event) => {
            if (event.key === 'Escape') {
              setOpen(false)
              setActiveIndex(-1)
              event.stopPropagation()
            }
            if (event.key === 'ArrowDown' && listboxOptions.length) {
              event.preventDefault()
              setOpen(true)
              setActiveIndex((index) => Math.min(index + 1, listboxOptions.length - 1))
            }
            if (event.key === 'ArrowUp' && listboxOptions.length) {
              event.preventDefault()
              setOpen(true)
              setActiveIndex((index) => index < 0
                ? listboxOptions.length - 1
                : Math.max(index - 1, 0))
            }
            if (event.key === 'Home' && open && listboxOptions.length) {
              event.preventDefault()
              setActiveIndex(0)
            }
            if (event.key === 'End' && open && listboxOptions.length) {
              event.preventDefault()
              setActiveIndex(listboxOptions.length - 1)
            }
            if (event.key === 'Enter' && open && activeIndex >= 0) {
              event.preventDefault()
              choose(listboxOptions[activeIndex])
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
          {listboxOptions.map((option, index) => (
            <li
              aria-selected={value === option.value}
              className={cn(
                'flex cursor-pointer items-center justify-between rounded-md px-2 py-2 text-left text-sm hover:bg-slate-50',
                value === option.value && 'bg-teal-50 text-teal-950',
                activeIndex === index && 'bg-slate-100',
                option.value === '' && 'text-slate-500',
              )}
              id={`${id}-option-${index}`}
              key={option.value || 'clear-selection'}
              onClick={() => choose(option)}
              onMouseDown={(event) => event.preventDefault()}
              role="option"
            >
              <span>{option.label}</span>
              {value === option.value && option.value !== '' ? (
                <Check aria-hidden="true" className="size-4" />
              ) : null}
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
