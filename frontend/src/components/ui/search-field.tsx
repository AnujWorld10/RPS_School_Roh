import { Search } from 'lucide-react'
import { useId } from 'react'
import { Input } from '@/components/ui/input'

type SearchFieldProps = {
  label: string
  placeholder?: string
  value?: string
  onChange?: (value: string) => void
}

export function SearchField({
  label,
  placeholder = 'Search',
  value,
  onChange,
}: SearchFieldProps) {
  const inputId = useId()

  return (
    <div className="relative w-full max-w-sm">
      <label className="sr-only" htmlFor={inputId}>
        {label}
      </label>
      <Search
        aria-hidden="true"
        className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-slate-400"
      />
      <Input
        className="h-10 pl-9"
        id={inputId}
        onChange={(event) => onChange?.(event.target.value)}
        placeholder={placeholder}
        value={value}
      />
    </div>
  )
}
