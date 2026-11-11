import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue } from '@/features/auth/auth-context'
import { admissionsApi, type Inquiry } from '@/features/admissions/admissions-api'
import { dashboardApi, type DashboardAdmissionStatus, type DashboardSummary } from '@/features/dashboard/dashboard-api'
import { DashboardPage } from './dashboard-page'

function authValue(permissions: string[]): AuthContextValue {
  return {
    user: {
      id: 1,
      first_name: 'School',
      last_name: 'Administrator',
      email: 'admin@example.invalid',
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
}

function renderDashboard(permissions: string[]) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AuthContext.Provider value={authValue(permissions)}>
          <DashboardPage />
        </AuthContext.Provider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function dashboardSummary(overrides: Partial<DashboardSummary> = {}): DashboardSummary {
  return {
    school_timezone: 'Asia/Kolkata',
    student_count: null,
    teacher_count: null,
    class_count: null,
    subject_count: null,
    inquiry_count: null,
    pending_admission_count: null,
    admissions_by_status: null,
    upcoming_interview_count: null,
    upcoming_interviews: null,
    ...overrides,
  }
}

const recentInquiry: Inquiry = {
  id: 5,
  inquiry_code: 'INQ202600005',
  serial_number: 5,
  first_name: 'Casey',
  middle_name: null,
  last_name: 'Student',
  gender: 'other',
  father_name: 'Parent Student',
  date_of_birth: '2016-01-03',
  student_mobile: null,
  parent_mobile: '+15555550115',
  email: 'parent@example.invalid',
  address: '1 School Street',
  last_school: 'Primary School',
  current_class: 'Grade 4',
  admission_for_class: 'Grade 5',
  last_school_percentage: null,
  admission_for_class_id: null,
  status: 'PENDING',
  rejection_reason: null,
  internal_notes: null,
  created_at: '2026-11-04T10:00:00Z',
  updated_at: null,
  status_timeline: [],
}

afterEach(() => {
  vi.restoreAllMocks()
})

describe('dashboard', () => {
  it('only displays metrics allowed by user permissions', async () => {
    const summary = vi.spyOn(dashboardApi, 'summary').mockResolvedValue(
      dashboardSummary({ student_count: 27 }),
    )
    const recentInquiries = vi.spyOn(admissionsApi.inquiries, 'list')
    renderDashboard(['students.read'])

    expect(await screen.findByText('27')).toBeInTheDocument()
    expect(screen.getByText('Students')).toBeInTheDocument()
    expect(screen.queryByText('Teachers')).not.toBeInTheDocument()
    expect(screen.queryByText('Admission applications by status')).not.toBeInTheDocument()
    expect(summary).toHaveBeenCalledOnce()
    expect(recentInquiries).not.toHaveBeenCalled()
  })

  it('shows backend admission counts and upcoming interview details in the school timezone', async () => {
    const counts: Record<DashboardAdmissionStatus, number> = {
      draft: 1,
      submitted: 2,
      document_pending: 3,
      document_verification: 4,
      approved: 5,
      rejected: 6,
    }
    vi.spyOn(dashboardApi, 'summary').mockResolvedValue(dashboardSummary({
      inquiry_count: 1,
      pending_admission_count: 10,
      admissions_by_status: counts,
      upcoming_interview_count: 6,
      upcoming_interviews: [{
        id: 12,
        inquiry_code: 'INQ202600012',
        student_name: 'Taylor Applicant',
        schedule_date: '2026-11-07',
        schedule_time: '10:30:00',
        location: 'Room 101',
        mode: 'OFFLINE',
      }],
    }))
    vi.spyOn(admissionsApi.inquiries, 'list').mockResolvedValue({
      items: [],
      pagination: { page: 1, limit: 5, total_records: 0, total_pages: 0 },
    })
    renderDashboard(['admissions.read', 'inquiries.read', 'interviews.read'])

    expect(await screen.findByText('10')).toBeInTheDocument()
    expect(screen.getByText('Pending admissions')).toBeInTheDocument()
    expect(await screen.findByText('Admission applications by status', {}, { timeout: 5000 })).toBeInTheDocument()
    expect(screen.getByText('Document review')).toBeInTheDocument()
    expect(screen.getAllByText('Upcoming interviews')).toHaveLength(2)
    expect(screen.getByText('Taylor Applicant · INQ202600012')).toBeInTheDocument()
    expect(screen.getByText(/2026-11-07 at 10:30:00 · OFFLINE/)).toBeInTheDocument()
    expect(screen.getByText(/school local time \(Asia\/Kolkata\)/i)).toBeInTheDocument()
    expect(screen.getByText('Showing the next 1 of 6 interviews.')).toBeInTheDocument()
  })

  it('preserves recent inquiries when summary metrics fail and reports the API error', async () => {
    vi.spyOn(dashboardApi, 'summary').mockRejectedValue(new Error('API unavailable'))
    vi.spyOn(admissionsApi.inquiries, 'list').mockResolvedValue({
      items: [recentInquiry],
      pagination: { page: 1, limit: 5, total_records: 1, total_pages: 1 },
    })
    renderDashboard(['students.read', 'inquiries.read'])

    expect(await screen.findByText('Casey Student')).toBeInTheDocument()
    expect(screen.getByText(/INQ202600005/)).toBeInTheDocument()
    expect(await screen.findByText('Dashboard summary unavailable')).toBeInTheDocument()
    expect(screen.getAllByText(/API unavailable/).length).toBeGreaterThan(0)
    expect(screen.getByRole('link', { name: 'View inquiries' })).toHaveAttribute('href', '/inquiries')
  })

  it('does not expose applicant interview details without inquiry permission', async () => {
    vi.spyOn(dashboardApi, 'summary').mockResolvedValue(dashboardSummary({
      upcoming_interview_count: 2,
      upcoming_interviews: null,
    }))
    renderDashboard(['interviews.read'])

    expect(await screen.findByText('2')).toBeInTheDocument()
    expect(screen.getByText('Upcoming interviews')).toBeInTheDocument()
    expect(screen.queryByText('Taylor Applicant')).not.toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'Manage interviews' })).not.toBeInTheDocument()
  })

  it('does not request metrics when the account has no relevant read permissions', () => {
    const summary = vi.spyOn(dashboardApi, 'summary')
    renderDashboard([])

    expect(screen.getByText('No dashboard metrics available')).toBeInTheDocument()
    expect(summary).not.toHaveBeenCalled()
  })
})
