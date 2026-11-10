import { useEffect, useId, useRef, useState, type ReactNode } from 'react'
import { NavLink } from 'react-router-dom'

type PublicNavDropdownProps = {
  label: string
  items: readonly { label: string; to: string }[]
  children?: ReactNode
  align?: 'left' | 'right'
  triggerClassName?: string
}

export function PublicNavDropdown({
  label,
  items,
  children,
  align = 'left',
  triggerClassName = '',
}: PublicNavDropdownProps) {
  const [open, setOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const triggerId = useId()
  const menuId = useId()

  useEffect(() => {
    if (!open) return

    function handlePointerDown(event: PointerEvent) {
      if (event.target instanceof Node && !containerRef.current?.contains(event.target)) {
        setOpen(false)
      }
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        setOpen(false)
        document.getElementById(triggerId)?.focus()
      }
    }

    document.addEventListener('pointerdown', handlePointerDown)
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('pointerdown', handlePointerDown)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [open, triggerId])

  const menuItemClass =
    'block rounded-md px-3 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-teal-50 hover:text-teal-950 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700'

  return (
    <div className="relative" ref={containerRef}>
      <button
        aria-controls={open ? menuId : undefined}
        aria-expanded={open}
        aria-haspopup="true"
        className={`flex min-h-10 items-center gap-1 rounded-md px-3 py-2 text-sm font-medium transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700 ${triggerClassName || 'text-slate-700 hover:bg-teal-50 hover:text-teal-950'}`}
        id={triggerId}
        onClick={() => setOpen((value) => !value)}
        type="button"
      >
        {label}
        <span aria-hidden="true" className={`text-xs transition-transform ${open ? 'rotate-180' : ''}`}>▾</span>
      </button>
      {open ? (
        <div
          aria-labelledby={triggerId}
          className={`absolute top-full z-50 mt-2 grid min-w-56 gap-1 rounded-xl border border-teal-100 bg-white p-2 shadow-xl shadow-slate-950/15 ${align === 'right' ? 'right-0' : 'left-0'}`}
          id={menuId}
        >
          {children}
          {items.map(({ label: itemLabel, to }) => (
            <NavLink className={menuItemClass} key={to} onClick={() => setOpen(false)} to={to}>
              {itemLabel}
            </NavLink>
          ))}
        </div>
      ) : null}
    </div>
  )
}
