import { fireEvent, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ErrorState, LoadingState } from './components/ui/async-state'
import App from './App'
import { AppProviders } from './providers'
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
  initialPath = '/',
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

describe('application layout', () => {
  it('renders the dashboard shell without claiming to load school data', () => {
    renderAuthenticatedApp()

    expect(screen.getByRole('heading', { name: 'Dashboard' })).toBeInTheDocument()
    expect(screen.getByText(/No school data is loaded in this phase/)).toBeInTheDocument()
    expect(screen.getByRole('navigation', { name: 'Breadcrumb' })).toBeInTheDocument()
  })

  it('navigates to a permitted module and updates the page title', async () => {
    const user = userEvent.setup()
    renderAuthenticatedApp()

    await user.click(screen.getAllByRole('link', { name: 'Teachers' })[0])

    expect(screen.getByRole('heading', { name: 'Teachers' })).toBeInTheDocument()
    expect(screen.getByText(/Manage teacher profiles, employment status/)).toBeInTheDocument()
  })

  it('opens and closes mobile navigation after selecting a route', async () => {
    const user = userEvent.setup()
    renderAuthenticatedApp()

    await user.click(screen.getByRole('button', { name: 'Open navigation' }))
    const mobileMenu = screen.getByRole('dialog', { name: 'Main navigation' })
    await user.click(within(mobileMenu).getByRole('link', { name: 'Students' }))

    expect(screen.getByRole('heading', { name: 'Students' })).toBeInTheDocument()
    expect(screen.queryByRole('dialog', { name: 'Main navigation' })).not.toBeInTheDocument()
  })

  it('collapses the desktop sidebar with an accessible toggle', async () => {
    const user = userEvent.setup()
    renderAuthenticatedApp()

    await user.click(screen.getByRole('button', { name: 'Toggle sidebar' }))

    expect(screen.getByRole('link', { name: 'Students' })).toHaveAttribute('title', 'Students')
    expect(screen.getByRole('button', { name: 'Expand sidebar' })).toBeInTheDocument()
  })

  it('shows the signed-in user and server-backed sign-out action', async () => {
    const user = userEvent.setup()
    renderAuthenticatedApp()

    await user.click(screen.getByRole('button', { name: 'Open account menu' }))

    expect(await screen.findByText('test-admin@example.invalid')).toBeInTheDocument()
    expect(screen.getByRole('menuitem', { name: 'Sign out' })).toBeInTheDocument()
  })

  it('hides unauthorized navigation and blocks a direct route', () => {
    renderAuthenticatedApp(['students.read'], '/salary')

    expect(screen.queryByRole('link', { name: 'Salary payments' })).not.toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Access restricted' })).toBeInTheDocument()
  })
})

describe('authentication routing', () => {
  it('redirects an unauthenticated visitor to the real sign-in form', async () => {
    render(
      <AppProviders>
        <App />
      </AppProviders>,
    )

    expect(await screen.findByRole('heading', { name: 'Sign in' })).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
    expect(screen.getByLabelText('Password')).toBeInTheDocument()
  })

  it('validates required login fields before making a request', async () => {
    const user = userEvent.setup()
    render(
      <AppProviders>
        <App />
      </AppProviders>,
    )
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
