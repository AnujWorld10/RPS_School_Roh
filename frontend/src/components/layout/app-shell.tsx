import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { Sidebar } from './sidebar'
import { Topbar } from './topbar'

export function AppShell() {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950">
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-20 hidden border-r border-slate-200 bg-white transition-[width] duration-200 lg:block',
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
              <Outlet />
            </div>
          </main>
          <footer className="border-t border-slate-200 bg-white px-4 py-4 text-center text-xs text-slate-500 sm:px-6 lg:px-8">
            RPS School Management <span aria-hidden="true">·</span> Frontend foundation
          </footer>
        </div>
      </div>
    </div>
  )
}
