import { useState } from 'react'
import { ChevronDown, Menu, UserRound } from 'lucide-react'
import { useLocation, useNavigate } from 'react-router-dom'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { Sidebar } from './sidebar'
import { allNavigationItems } from './navigation'
import { useAuth } from '@/features/auth/auth-context'
import { toApiError } from '@/lib/api/api-error'

type TopbarProps = {
  onToggleSidebar: () => void
}

export function Topbar({ onToggleSidebar }: TopbarProps) {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout, isLoggingOut } = useAuth()
  const [mobileNavigationOpen, setMobileNavigationOpen] = useState(false)
  const currentPage = allNavigationItems.find((item) => item.path === location.pathname)
  const pageTitle = currentPage?.label ?? 'Page not found'
  const fullName = user ? `${user.first_name} ${user.last_name}`.trim() : 'Account'

  async function handleLogout() {
    try {
      await logout()
    } catch (error) {
      navigate('/login', {
        replace: true,
        state: { logoutError: toApiError(error).message },
      })
    }
  }

  return (
    <header className="sticky top-0 z-30 flex h-[72px] shrink-0 items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur sm:px-6 lg:px-8">
      <div className="flex min-w-0 items-center gap-3">
        <Sheet onOpenChange={setMobileNavigationOpen} open={mobileNavigationOpen}>
          <SheetTrigger
            aria-label="Open navigation"
            className="inline-flex size-10 items-center justify-center rounded-lg border border-slate-200 text-slate-700 hover:bg-slate-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 lg:hidden"
          >
            <Menu aria-hidden="true" size={19} />
          </SheetTrigger>
          <SheetContent className="p-0" side="left">
            <SheetTitle className="sr-only">Main navigation</SheetTitle>
            <Sidebar onNavigate={() => setMobileNavigationOpen(false)} />
          </SheetContent>
        </Sheet>

        <Button
          aria-label="Toggle sidebar"
          className="hidden text-slate-600 lg:inline-flex"
          onClick={onToggleSidebar}
          size="icon"
          variant="ghost"
        >
          <Menu aria-hidden="true" size={19} />
        </Button>
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-slate-950 sm:text-base">{pageTitle}</p>
          <nav aria-label="Breadcrumb" className="mt-0.5 hidden items-center gap-2 text-xs text-slate-500 sm:flex">
            <span>School administration</span>
            <span aria-hidden="true">/</span>
            <span aria-current="page" className="truncate text-slate-700">
              {pageTitle}
            </span>
          </nav>
        </div>
      </div>

      <DropdownMenu>
        <DropdownMenuTrigger
          aria-label="Open account menu"
          className="flex items-center gap-2 rounded-lg p-1.5 text-left hover:bg-slate-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
        >
          <span className="flex size-9 items-center justify-center rounded-full bg-slate-100 text-slate-600">
            <UserRound aria-hidden="true" size={17} />
          </span>
          <span className="hidden sm:block">
            <span className="block max-w-48 truncate text-xs font-medium text-slate-800">
              {fullName}
            </span>
            <span className="block max-w-48 truncate text-[0.68rem] text-slate-500">
              {user?.email}
            </span>
          </span>
          <ChevronDown aria-hidden="true" className="hidden size-4 text-slate-400 sm:block" />
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuGroup>
            <DropdownMenuLabel>Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            {user?.roles.length ? (
              <>
                <DropdownMenuLabel className="font-normal text-muted-foreground">
                  {user.roles.join(', ')}
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
              </>
            ) : null}
            <DropdownMenuItem disabled={isLoggingOut} onClick={() => void handleLogout()}>
              {isLoggingOut ? 'Signing out…' : 'Sign out'}
            </DropdownMenuItem>
          </DropdownMenuGroup>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  )
}
