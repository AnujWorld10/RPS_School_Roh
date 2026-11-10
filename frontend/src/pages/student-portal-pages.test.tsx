import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from '@/App'
import { AuthContext, type AuthContextValue } from '@/features/auth/auth-context'
import { registerStudentPortal } from '@/features/auth/auth-api'
import { studentPortalApi } from '@/features/school/student-portal-api'

vi.mock('@/features/auth/auth-api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/features/auth/auth-api')>()
  return { ...actual, registerStudentPortal: vi.fn() }
})

vi.mock('@/features/school/student-portal-api', () => ({
  studentPortalApi: {
    profile: vi.fn(),
    fees: vi.fn(),
  },
}))

const unauthenticatedContext: AuthContextValue = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  isLoggingIn: false,
  isLoggingOut: false,
  sessionExpired: false,
  login: vi.fn(),
  logout: vi.fn(),
}

const studentContext: AuthContextValue = {
  user: {
    id: 12,
    first_name: 'Aarav',
    last_name: 'Sharma',
    email: 'student@example.test',
    phone: null,
    roles: ['STUDENT'],
    permissions: ['students.read'],
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

function renderApp(path: string, auth = unauthenticatedContext) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[path]}>
        <AuthContext.Provider value={auth}>
          <App />
        </AuthContext.Provider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

afterEach(() => {
  vi.clearAllMocks()
})

describe('student portal registration and login', () => {
  it('offers student sign-up from the public sign-in menu', async () => {
    const user = userEvent.setup()
    renderApp('/school/home')

    await user.click(screen.getByRole('button', { name: 'Sign in' }))
    expect(screen.getByRole('link', { name: 'Sign up as a New Student' }))
      .toHaveAttribute('href', '/student/register')
  })

  it('validates registration and reports the issued student ID', async () => {
    const user = userEvent.setup()
    vi.mocked(registerStudentPortal).mockResolvedValue({
      student_id: 'RPS00001',
      email: 'student@example.test',
    })
    renderApp('/student/register')

    expect(await screen.findByRole('heading', { name: 'Create a student account' })).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Create student account' }))
    expect(await screen.findByText('Enter the admission ID issued by the school.')).toBeInTheDocument()
    expect(screen.getByText('Enter a valid registered email address.')).toBeInTheDocument()

    await user.type(screen.getByLabelText('Admission ID / Student ID'), 'RPS00001')
    await user.type(screen.getByLabelText('Registered email address'), 'student@example.test')
    await user.type(screen.getByLabelText('Create password'), 'StrongStudent@123')
    await user.type(screen.getByLabelText('Confirm password'), 'StrongStudent@123')
    await user.click(screen.getByRole('button', { name: 'Create student account' }))

    expect(await screen.findByText('RPS00001')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Continue to student login' }))
      .toHaveAttribute('href', '/login?portal=student')
    expect(registerStudentPortal).toHaveBeenCalledWith({
      admission_id: 'RPS00001',
      email: 'student@example.test',
      password: 'StrongStudent@123',
      confirm_password: 'StrongStudent@123',
    })
  })

  it('uses the student ID login flow instead of email login', async () => {
    const user = userEvent.setup()
    const login = vi.fn().mockResolvedValue(undefined)
    renderApp('/login?portal=student', { ...unauthenticatedContext, login })

    expect(await screen.findByLabelText('Student ID')).toBeInTheDocument()
    await user.type(screen.getByLabelText('Student ID'), 'RPS00001')
    await user.type(screen.getByLabelText('Password'), 'StrongStudent@123')
    await user.click(screen.getByRole('button', { name: 'Sign in' }))

    expect(login).toHaveBeenCalledWith({
      student_id: 'RPS00001',
      password: 'StrongStudent@123',
      portal: 'student',
    })
  })
})

describe('student dashboard', () => {
  it('shows only the linked student profile and actual fee schedule values', async () => {
    vi.mocked(studentPortalApi.profile).mockResolvedValue({
      student_id: 'RPS00001',
      admission_id: 'RPS00001',
      first_name: 'Aarav',
      middle_name: null,
      last_name: 'Sharma',
      father_name: 'Raj Sharma',
      mother_name: null,
      date_of_birth: '2015-05-14',
      gender: 'male',
      class_name: 'Grade 5',
      section: 'A',
      academic_year: '2026-2027',
      email: 'student@example.test',
      phone: '9000000001',
      address: '12 School Road',
      admission_date: '2026-10-01T10:00:00Z',
      student_photo_url: null,
      status: 'active',
    })
    vi.mocked(studentPortalApi.fees).mockResolvedValue({
      student_id: 'RPS00001',
      class_id: 5,
      academic_year: '2026-2027',
      admission_fee_structure: {
        structure_name: '2026 Admission',
        total_amount: 15000,
        components: [
          {
            id: 1,
            fee_name: 'Registration fee',
            amount: 15000,
            is_optional: false,
            is_refundable: false,
          },
        ],
      },
      monthly_fee_structure: {
        structure_name: 'Grade 5 fees',
        mandatory_annual_total: 60000,
        optional_annual_total: 0,
        total_annual_amount: 60000,
        components: [
          {
            id: 2,
            fee_name: 'Tuition',
            amount: 5000,
            billing_frequency: 'MONTHLY',
            is_optional: false,
          },
        ],
      },
      payment_records_available: false,
      paid_amount: null,
      pending_amount: null,
      upcoming_due_date: null,
      payment_status: null,
      billing_message: 'Invoices and payment collection are not configured.',
    })

    renderApp('/portal/student', studentContext)

    expect(await screen.findByRole('heading', { name: 'Student dashboard' })).toBeInTheDocument()
    expect(await screen.findAllByText('RPS00001')).toHaveLength(2)
    expect(screen.getByText('Raj Sharma')).toBeInTheDocument()
    expect(await screen.findByText('Registration fee')).toBeInTheDocument()
    expect(await screen.findByText('Tuition')).toBeInTheDocument()
    expect(screen.getByText('Invoices and payment collection are not configured.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Download Monthly Fee PDF' })).toBeDisabled()
  })
})
