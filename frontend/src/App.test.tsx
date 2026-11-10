import { fireEvent, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ErrorState, LoadingState } from './components/ui/async-state'
import App from './App'
import { AuthContext, type AuthContextValue } from './features/auth/auth-context'
import { ConfirmDialog } from './components/ui/confirm-dialog'

const adminPermissions = [
  'students.read',
  'teachers.read',
  'teachers.update',
  'teachers.salary.read',
  'teachers.salary.pay',
  'classes.read',
  'subjects.read',
  'inquiries.read',
  'interviews.read',
  'admissions.read',
  'admissions.update',
  'admissions.verify_documents',
]

function renderAuthenticatedApp(
  permissions: string[] = adminPermissions,
  initialPath = '/dashboard',
) {
  const authValue: AuthContextValue = {
    user: {
      id: 1,
      first_name: 'Test',
      last_name: 'Administrator',
      email: 'test-admin@example.invalid',
      phone: null,
      roles: ['ADMIN'],
      permissions,
      status: 'active',
    },
    isAuthenticated: true,
    isLoading: false,
    isLoggingIn: false,
    isLoggingOut: false,
    sessionExpired: false,
    login: vi.fn(),
    logout: vi.fn(),
  }

  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={[initialPath]}>
        <AuthContext.Provider value={authValue}>
          <App />
        </AuthContext.Provider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function renderUnauthenticatedApp(initialPath = '/') {
  const authValue: AuthContextValue = {
    user: null,
    isAuthenticated: false,
    isLoading: false,
    isLoggingIn: false,
    isLoggingOut: false,
    sessionExpired: false,
    login: vi.fn(),
    logout: vi.fn(),
  }

  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={[initialPath]}>
        <AuthContext.Provider value={authValue}>
          <App />
        </AuthContext.Provider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('application layout', () => {
  it('renders the dashboard shell without loading metrics without read permissions', async () => {
    renderAuthenticatedApp([], '/dashboard')

    expect(await screen.findByRole('heading', { name: 'Dashboard' })).toBeInTheDocument()
    expect(screen.getByText(/does not have permission to read the school or admissions summary APIs/)).toBeInTheDocument()
    expect(screen.getByRole('navigation', { name: 'Breadcrumb' })).toBeInTheDocument()
  })

  it('navigates to a permitted module and updates the page title', async () => {
    const user = userEvent.setup()
    renderAuthenticatedApp()

    await user.click((await screen.findAllByRole('link', { name: 'Teachers' }))[0])

    expect(await screen.findByRole('heading', { name: 'Teachers' })).toBeInTheDocument()
    expect(screen.getByText(/Manage teacher profiles, employment status/)).toBeInTheDocument()
  })

  it('opens and closes mobile navigation after selecting a route', async () => {
    const user = userEvent.setup()
    renderAuthenticatedApp()

    await user.click(await screen.findByRole('button', { name: 'Open navigation' }))
    const mobileMenu = screen.getByRole('dialog', { name: 'Main navigation' })
    await user.click(within(mobileMenu).getByRole('link', { name: 'Students' }))

    expect(await screen.findByRole('heading', { name: 'Students' })).toBeInTheDocument()
    expect(screen.queryByRole('dialog', { name: 'Main navigation' })).not.toBeInTheDocument()
  })

  it('collapses the desktop sidebar with an accessible toggle', async () => {
    const user = userEvent.setup()
    renderAuthenticatedApp()

    await user.click(await screen.findByRole('button', { name: 'Toggle sidebar' }))

    expect(screen.getByRole('link', { name: 'Students' })).toHaveAttribute('title', 'Students')
    expect(screen.getByRole('button', { name: 'Expand sidebar' })).toBeInTheDocument()
  })

  it('shows the signed-in user and server-backed sign-out action', async () => {
    const user = userEvent.setup()
    renderAuthenticatedApp()

    await user.click(await screen.findByRole('button', { name: 'Open account menu' }))

    expect(await screen.findByRole('menuitem', { name: 'Sign out' })).toBeInTheDocument()
    expect(screen.getByText('test-admin@example.invalid')).toBeInTheDocument()
  })

  it('hides unauthorized navigation and does not expose unfinished module routes', async () => {
    renderAuthenticatedApp(['students.read'], '/salary')

    expect(screen.queryByRole('link', { name: 'Salary payments' })).not.toBeInTheDocument()
    expect(await screen.findByRole('heading', { name: 'Page not found' })).toBeInTheDocument()
  })
})

describe('authentication routing', () => {
  it('opens the public school homepage for an unauthenticated visitor at the home URL', async () => {
    renderUnauthenticatedApp()

    expect(await screen.findByRole('heading', { name: 'Welcome to RPS School' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'A pathway for every stage' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Stay informed' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Life at RPS' })).toBeInTheDocument()
    expect(screen.getAllByRole('link', { name: 'Start an inquiry' })[0]).toHaveAttribute('href', '/apply')
  })

  it('places the public admission portal link at the top of the staff sign-in page', async () => {
    renderUnauthenticatedApp('/login')

    expect(await screen.findByRole('heading', { name: 'Sign in' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Open the public admission portal' })).toHaveAttribute('href', '/apply')
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
    expect(screen.getByLabelText('Password')).toBeInTheDocument()
    expect(screen.getByRole('navigation', { name: 'School website' })).toBeInTheDocument()
  })

  it('validates required login fields before making a request', async () => {
    const user = userEvent.setup()
    renderUnauthenticatedApp('/login')
    await screen.findByRole('heading', { name: 'Sign in' })

    await user.click(screen.getByRole('button', { name: 'Sign in' }))

    expect(await screen.findByText('Enter a valid email address.')).toBeInTheDocument()
    expect(screen.getByText('Password is required.')).toBeInTheDocument()
  })
})

describe('shared UI states', () => {
  it('keeps a confirmation open and displays an API failure', async () => {
    const user = userEvent.setup()
    const onConfirm = vi.fn().mockRejectedValue(new Error('The operation was rejected.'))
    render(
      <ConfirmDialog
        description="Delete this record?"
        onConfirm={onConfirm}
        title="Confirm deletion"
        trigger={<button type="button">Delete record</button>}
      />,
    )

    await user.click(screen.getByRole('button', { name: 'Delete record' }))
    await user.click(screen.getByRole('button', { name: 'Continue' }))

    expect(await screen.findByText('The operation was rejected.')).toBeInTheDocument()
    expect(screen.getByRole('dialog', { name: 'Confirm deletion' })).toBeInTheDocument()
    expect(onConfirm).toHaveBeenCalledOnce()
  })

  it('lets the user cancel a confirmation without running the action', async () => {
    const user = userEvent.setup()
    const onConfirm = vi.fn()
    render(
      <ConfirmDialog
        description="Delete this record?"
        onConfirm={onConfirm}
        title="Confirm deletion"
        trigger={<button type="button">Delete record</button>}
      />,
    )

    await user.click(screen.getByRole('button', { name: 'Delete record' }))
    await user.click(screen.getByRole('button', { name: 'Cancel' }))

    expect(screen.queryByRole('dialog', { name: 'Confirm deletion' })).not.toBeInTheDocument()
    expect(onConfirm).not.toHaveBeenCalled()
  })

  it('announces loading content to assistive technology', () => {
    render(<LoadingState label="Loading classes" />)
    expect(screen.getByRole('status')).toHaveTextContent('Loading classes')
  })

  it('exposes an error retry action', () => {
    const onRetry = vi.fn()
    render(<ErrorState description="Request failed" onRetry={onRetry} />)
    fireEvent.click(screen.getByRole('button', { name: 'Try again' }))
    expect(onRetry).toHaveBeenCalledOnce()
  })
})
