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
        hasAnyPermission(user?.permissions ?? [], item.anyPermission ?? [])
        && (item.allPermissions ?? []).every((permission) => user?.permissions?.includes(permission))
        && (!item.anyRole || item.anyRole.some((role) => user?.roles.includes(role))),
      ),
    }))
    .filter((group) => group.items.length > 0)

  return (
    <div className="flex h-full flex-col bg-sidebar text-sidebar-foreground">
      <div
        className={cn(
          'flex h-[72px] shrink-0 items-center border-b border-sidebar-border px-5',
          collapsed && 'justify-center px-3',
        )}
      >
        <NavLink
          aria-label="RPS School Management home"
          className="flex min-w-0 items-center gap-3"
          onClick={onNavigate}
          to="/dashboard"
        >
          <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-amber-400 text-slate-950 shadow-sm shadow-amber-950/20">
            <GraduationCap aria-hidden="true" size={20} />
          </span>
          {!collapsed ? (
            <span className="min-w-0">
              <span className="block truncate text-sm font-semibold text-white">RPS School</span>
              <span className="mt-0.5 block truncate text-xs text-slate-300">Administration</span>
            </span>
          ) : null}
        </NavLink>
      </div>

      <nav aria-label="Main navigation" className="flex-1 space-y-6 overflow-y-auto px-3 py-5">
        {visibleGroups.map((group) => (
          <section aria-label={group.label} key={group.label}>
            {!collapsed ? (
              <h2 className="mb-2 px-3 text-[0.68rem] font-semibold uppercase tracking-[0.13em] text-teal-200/80">
                {group.label}
              </h2>
            ) : null}
            <div className="space-y-1">
              {group.items.map(({ icon: Icon, label, path }) => (
                <NavLink
                  aria-label={collapsed ? label : undefined}
                  className={({ isActive }) =>
                    cn(
                      'group flex min-h-10 items-center gap-3 rounded-lg px-3 text-sm font-medium text-slate-300 transition-colors hover:bg-sidebar-accent hover:text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sidebar-ring',
                      isActive && 'bg-sidebar-primary font-semibold text-sidebar-primary-foreground shadow-sm hover:bg-sidebar-primary',
                      collapsed && 'justify-center px-0',
                    )
                  }
                  end={path === '/dashboard'}
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
        <div className="hidden border-t border-sidebar-border p-3 lg:block">
          <Button
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            className={cn('w-full justify-start text-slate-300 hover:bg-sidebar-accent hover:text-white', collapsed && 'justify-center')}
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
