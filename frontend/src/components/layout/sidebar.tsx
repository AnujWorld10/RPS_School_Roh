import { ChevronLeft, GraduationCap } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/features/auth/auth-context'
import { hasAnyPermission } from '@/features/auth/permissions'
import { cn } from '@/lib/utils'
import { navigationGroups } from './navigation'

type SidebarProps = {
  collapsed?: boolean
  onNavigate?: () => void
  onToggleCollapse?: () => void
}

export function Sidebar({ collapsed = false, onNavigate, onToggleCollapse }: SidebarProps) {
  const { user } = useAuth()
  const visibleGroups = navigationGroups
    .map((group) => ({
      ...group,
      items: group.items.filter((item) =>
        hasAnyPermission(user?.permissions ?? [], item.anyPermission ?? []),
      ),
    }))
    .filter((group) => group.items.length > 0)

  return (
    <div className="flex h-full flex-col bg-white">
      <div
        className={cn(
          'flex h-[72px] shrink-0 items-center border-b border-slate-200 px-5',
          collapsed && 'justify-center px-3',
        )}
      >
        <NavLink
          aria-label="RPS School Management home"
          className="flex min-w-0 items-center gap-3"
          onClick={onNavigate}
          to="/"
        >
          <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-indigo-700 text-white">
            <GraduationCap aria-hidden="true" size={20} />
          </span>
          {!collapsed ? (
            <span className="min-w-0">
              <span className="block truncate text-sm font-semibold text-slate-950">RPS School</span>
              <span className="mt-0.5 block truncate text-xs text-slate-500">Administration</span>
            </span>
          ) : null}
        </NavLink>
      </div>

      <nav aria-label="Main navigation" className="flex-1 space-y-6 overflow-y-auto px-3 py-5">
        {visibleGroups.map((group) => (
          <section aria-label={group.label} key={group.label}>
            {!collapsed ? (
              <h2 className="mb-2 px-3 text-[0.68rem] font-semibold uppercase tracking-[0.13em] text-slate-400">
                {group.label}
              </h2>
            ) : null}
            <div className="space-y-1">
              {group.items.map(({ icon: Icon, label, path }) => (
                <NavLink
                  aria-label={collapsed ? label : undefined}
                  className={({ isActive }) =>
                    cn(
                      'group flex min-h-10 items-center gap-3 rounded-lg px-3 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-950 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600',
                      isActive && 'bg-indigo-50 text-indigo-800 hover:bg-indigo-50',
                      collapsed && 'justify-center px-0',
                    )
                  }
                  end={path === '/'}
                  key={path}
                  onClick={onNavigate}
                  title={collapsed ? label : undefined}
                  to={path}
                >
                  <Icon aria-hidden="true" className="size-[18px] shrink-0" strokeWidth={1.8} />
                  {!collapsed ? <span className="truncate">{label}</span> : null}
                </NavLink>
              ))}
            </div>
          </section>
        ))}
      </nav>

      {onToggleCollapse ? (
        <div className="hidden border-t border-slate-200 p-3 lg:block">
          <Button
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            className={cn('w-full justify-start text-slate-500', collapsed && 'justify-center')}
            onClick={onToggleCollapse}
            size="sm"
            variant="ghost"
          >
            <ChevronLeft
              aria-hidden="true"
              className={cn('size-4 transition-transform', collapsed && 'rotate-180')}
            />
            {!collapsed ? <span>Collapse menu</span> : null}
          </Button>
        </div>
      ) : null}
    </div>
  )
}
