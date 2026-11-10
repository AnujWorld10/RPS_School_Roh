import { Suspense, useState } from 'react'
import { Outlet } from 'react-router-dom'
import { LoadingState } from '@/components/ui/async-state'
import { cn } from '@/lib/utils'
import { Sidebar } from './sidebar'
import { Topbar } from './topbar'

export function AppShell() {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div className="min-h-screen bg-background text-foreground">
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-20 hidden border-r border-sidebar-border bg-sidebar text-sidebar-foreground shadow-xl shadow-slate-950/10 transition-[width] duration-200 lg:block',
          collapsed ? 'w-[76px]' : 'w-[260px]',
        )}
      >
        <Sidebar collapsed={collapsed} onToggleCollapse={() => setCollapsed((value) => !value)} />
      </aside>
      <div className={cn('min-h-screen transition-[padding] duration-200', collapsed ? 'lg:pl-[76px]' : 'lg:pl-[260px]')}>
        <div className="flex min-h-screen flex-col">
          <Topbar onToggleSidebar={() => setCollapsed((value) => !value)} />
          <main className="flex-1 px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
            <div className="mx-auto w-full max-w-[1440px]">
              <Suspense fallback={<LoadingState label="Loading page" />}>
                <Outlet />
              </Suspense>
            </div>
          </main>
          <footer className="border-t border-border/80 bg-white/80 px-4 py-4 text-center text-xs text-muted-foreground sm:px-6 lg:px-8">
            RPS School Management <span aria-hidden="true">·</span> Frontend foundation
          </footer>
        </div>
      </div>
    </div>
  )
}
