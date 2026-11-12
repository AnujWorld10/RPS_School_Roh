import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue } from '@/features/auth/auth-context'
import { AdmissionDocumentsPanel } from '@/features/admissions/admission-documents-panel'
import {
  admissionsApi,
  REQUIRED_ADMISSION_DOCUMENT_TYPES,
  type Admission,
  type Inquiry,
  type Interview,
} from '@/features/admissions/admissions-api'
import { ApiError } from '@/lib/api/api-error'
import { schoolApi } from '@/features/school/school-api'
import { InquiriesPage } from '@/pages/inquiries-page'
import { InterviewsPage } from '@/pages/interviews-page'
import { AdmissionsPage } from '@/pages/admissions-page'

const inquiry: Inquiry = {
  id: 8,
  inquiry_code: 'INQ202600008',
  serial_number: 8,
  first_name: 'Taylor',
  middle_name: null,
  last_name: 'Example',
  gender: 'female',
  father_name: 'Morgan Example',
  date_of_birth: '2016-03-12',
  student_mobile: null,
  parent_mobile: '+15555550112',
  email: 'parent@example.com',
  address: '12 North School Road',
  last_school: 'Example Primary',
  current_class: 'Grade 4',
  admission_for_class: 'Grade 5',
  last_school_percentage: null,
  admission_for_class_id: null,
  status: 'PROCESSING',
  rejection_reason: null,
  internal_notes: null,
  created_at: '2026-11-01T10:00:00Z',
  updated_at: null,
  status_timeline: [],
}

const interview: Interview = {
  id: 15,
  inquiry_id: inquiry.id,
  schedule_date: '2026-11-06',
  schedule_time: '10:00:00',
  location: 'Room 4',
  mode: 'OFFLINE',
  interviewer_teacher_id: null,
  remarks: null,
  result: 'SCHEDULED',
}

function authValue(permissions: string[]): AuthContextValue {
  return {
    user: {
      id: 1,
      first_name: 'Admission',
      last_name: 'Officer',
      email: 'officer@example.com',
      phone: null,
      roles: ['ADMISSION_OFFICER'],
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

function renderWithAuth(ui: React.ReactNode, permissions: string[]) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AuthContext.Provider value={authValue(permissions)}>{ui}</AuthContext.Provider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

afterEach(() => {
  vi.restoreAllMocks()
})

describe('admission lifecycle pages', () => {
  it('lets staff choose section and academic year separately during enrollment', async () => {
    const user = userEvent.setup()
    const admission: Admission = {
      id: 12,
      admission_code: 'ADM202600012',
      inquiry_id: inquiry.id,
      class_id: 2,
      class_name: '5th Grade',
      section: null,
      academic_year: '2026-2027',
      status: 'approved',
      permanent_address: null,
      student_aadhaar_masked: null,
      parent_aadhaar_masked: null,
      last_school_marks: null,
      last_school_percentage: null,
      last_school_id_or_roll_number: null,
      temporary_address: null,
      nationality: null,
      disability: null,
      blood_group: null,
      reason_for_school_change: null,
      rejection_reason: null,
      notes: null,
      student_id: null,
      documents: REQUIRED_ADMISSION_DOCUMENT_TYPES.map((document_type, index) => ({
        id: index + 1,
        admission_id: 12,
        document_type,
        file_name: `${document_type}.pdf`,
        verification_status: 'VERIFIED',
        rejection_reason: null,
        verified_at: '2026-11-11T00:00:00Z',
      })),
    }
    vi.spyOn(admissionsApi.admissions, 'list').mockResolvedValue({
      items: [admission],
      pagination: { page: 1, limit: 10, total_records: 1, total_pages: 1 },
    })
    vi.spyOn(admissionsApi.admissions, 'get').mockResolvedValue(admission)
    vi.spyOn(admissionsApi.admissions, 'requiredDocuments').mockResolvedValue({
      required: REQUIRED_ADMISSION_DOCUMENT_TYPES,
    })
    const enroll = vi.spyOn(admissionsApi.admissions, 'enroll').mockResolvedValue({
      student_id: 22,
      student_code: 'RPS00022',
      admission_id: admission.id,
      admission_code: 'RPS00022',
      inquiry_code: inquiry.inquiry_code,
      class_id: 9,
      section: 'B',
      academic_year: '2025-2026',
      roll_number: 1,
    })
    vi.spyOn(schoolApi.classes, 'list').mockResolvedValue({
      items: [
        { id: 2, class_teacher_id: null, name: '5th Grade', section: 'A', academic_year: '2026-2027', capacity: 40, status: 'active' },
        { id: 9, class_teacher_id: null, name: '5th Grade', section: 'B', academic_year: '2025-2026', capacity: 40, status: 'active' },
      ],
      pagination: { page: 1, limit: 100, total_records: 2, total_pages: 1 },
    })
    renderWithAuth(<AdmissionsPage />, ['admissions.read', 'enrollment.create', 'classes.read'])

    await user.click(await screen.findByRole('button', { name: 'Review' }))
    await user.click(await screen.findByRole('button', { name: 'Enroll student' }))
    const yearSelect = await screen.findByRole('combobox', { name: 'Academic year' })
    const sectionSelect = screen.getByRole('combobox', { name: 'Section' })
    expect(yearSelect).toHaveValue('')
    expect(sectionSelect).toBeDisabled()
    await user.selectOptions(yearSelect, '2025-2026')
    await user.selectOptions(sectionSelect, 'B')
    await user.click(screen.getByRole('button', { name: 'Confirm enrollment' }))

    await waitFor(() => expect(enroll).toHaveBeenCalledWith(admission.id, 9))
  })

  it('rejects a future inquiry date of birth before sending the request', async () => {
    const user = userEvent.setup()
    vi.spyOn(admissionsApi.inquiries, 'list').mockResolvedValue({
      items: [],
      pagination: { page: 1, limit: 10, total_records: 0, total_pages: 0 },
    })
    vi.spyOn(admissionsApi.inquiries, 'create')
    vi.spyOn(schoolApi.classes, 'list').mockResolvedValue({
      items: [],
      pagination: { page: 1, limit: 100, total_records: 0, total_pages: 0 },
    })
    renderWithAuth(<InquiriesPage />, ['inquiries.read', 'inquiries.create', 'classes.read'])

    await user.click(screen.getByRole('button', { name: 'Create inquiry' }))
    await user.type(screen.getByLabelText(/Student first name/), 'Taylor')
    await user.type(screen.getByLabelText(/Student last name/), 'Example')
    await user.selectOptions(screen.getByLabelText(/Gender/), 'female')
    await user.type(screen.getByLabelText(/Parent or guardian name/), 'Morgan Example')
    const dateOfBirth = screen.getByLabelText(/Date of birth/)
    expect(dateOfBirth).toHaveAttribute('max', expect.stringMatching(/^\d{4}-\d{2}-\d{2}$/))
    fireEvent.change(dateOfBirth, { target: { value: '2999-01-01' } })
    await user.type(screen.getByLabelText(/Parent mobile/), '+15555550112')
    await user.type(screen.getByLabelText(/Parent email/), 'parent@example.com')
    await user.type(screen.getByLabelText(/Residential address/), '12 North School Road')
    await user.type(screen.getByLabelText(/Last school/), 'Example Primary')
    await user.type(screen.getByLabelText(/Current class or grade/), 'Grade 4')
    await user.type(screen.getByLabelText(/Requested class or grade/), 'Grade 5')
    await user.click(screen.getByRole('button', { name: 'Submit inquiry' }))

    expect(await screen.findByText('Date of birth cannot be in the future.')).toBeInTheDocument()
    expect(dateOfBirth).toHaveAttribute('aria-invalid', 'true')
    expect(admissionsApi.inquiries.create).not.toHaveBeenCalled()
  })

  it('shows duplicate inquiry conflicts and preserves the submitted form values', async () => {
    const user = userEvent.setup()
    vi.spyOn(admissionsApi.inquiries, 'list').mockResolvedValue({
      items: [],
      pagination: { page: 1, limit: 10, total_records: 0, total_pages: 0 },
    })
    vi.spyOn(admissionsApi.inquiries, 'create').mockRejectedValue(
      new ApiError('Student inquiry already exists. Please contact school administration.', {
        status: 409,
        code: 'RESOURCE_CONFLICT',
      }),
    )
    vi.spyOn(schoolApi.classes, 'list').mockResolvedValue({
      items: [],
      pagination: { page: 1, limit: 100, total_records: 0, total_pages: 0 },
    })
    renderWithAuth(<InquiriesPage />, ['inquiries.read', 'inquiries.create', 'classes.read'])

    await user.click(screen.getByRole('button', { name: 'Create inquiry' }))
    await user.type(screen.getByLabelText(/Student first name/), 'Taylor')
    await user.type(screen.getByLabelText(/Student last name/), 'Example')
    await user.selectOptions(screen.getByLabelText(/Gender/), 'female')
    await user.type(screen.getByLabelText(/Parent or guardian name/), 'Morgan Example')
    await user.type(screen.getByLabelText(/Date of birth/), '2016-03-12')
    await user.type(screen.getByLabelText(/Parent mobile/), '+15555550112')
    await user.type(screen.getByLabelText(/Parent email/), 'parent@example.com')
    await user.type(screen.getByLabelText(/Residential address/), '12 North School Road')
    await user.type(screen.getByLabelText(/Last school/), 'Example Primary')
    await user.type(screen.getByLabelText(/Current class or grade/), 'Grade 4')
    await user.type(screen.getByLabelText(/Requested class or grade/), 'Grade 5')
    await user.click(screen.getByRole('button', { name: 'Submit inquiry' }))

    expect(await screen.findByText(/possible duplicate inquiry was rejected/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Student first name/)).toHaveValue('Taylor')
    expect(screen.getByLabelText(/Parent email/)).toHaveValue('parent@example.com')
  })

  it('schedules an interview only through the selected inquiry workflow', async () => {
    const user = userEvent.setup()
    vi.spyOn(admissionsApi.inquiries, 'list').mockResolvedValue({
      items: [inquiry],
      pagination: { page: 1, limit: 10, total_records: 1, total_pages: 1 },
    })
    vi.spyOn(admissionsApi.inquiries, 'get').mockResolvedValue(inquiry)
    vi.spyOn(admissionsApi.interviews, 'listForInquiry').mockResolvedValue([])
    const schedule = vi.spyOn(admissionsApi.interviews, 'schedule').mockResolvedValue(interview)
    vi.spyOn(schoolApi.teachers, 'list').mockResolvedValue({
      items: [],
      pagination: { page: 1, limit: 100, total_records: 0, total_pages: 0 },
    })
    renderWithAuth(<InterviewsPage />, ['inquiries.read', 'interviews.read', 'interviews.schedule'])

    expect(await screen.findByRole('table', { name: 'Inquiries available for interview' })).toBeInTheDocument()
    expect(screen.getByRole('textbox', { name: 'Search inquiries' })).toBeVisible()
    expect(screen.getByRole('combobox', { name: 'Filter inquiries by status' })).toBeVisible()
    expect(screen.getByRole('columnheader', { name: 'Grade / class' })).toBeInTheDocument()
    expect(screen.getByRole('cell', { name: 'Grade 5' })).toBeInTheDocument()
    await user.click(await screen.findByRole('button', { name: 'View interviews' }))
    await screen.findByRole('heading', { name: /INQ202600008/ })
    await user.click(screen.getByRole('button', { name: 'Schedule interview' }))
    await user.type(screen.getByLabelText(/Interview date/), '2026-11-06')
    await user.type(screen.getByLabelText(/Interview start time/), '10:00')
    await user.type(screen.getByLabelText(/Location or meeting details/), 'Room 4')
    await user.click(screen.getByRole('button', { name: 'Schedule interview' }))

    await waitFor(() => expect(schedule).toHaveBeenCalledWith(inquiry.id, {
      schedule_date: '2026-11-06',
      schedule_time: '10:00',
      location: 'Room 4',
      mode: 'OFFLINE',
      remarks: undefined,
    }))
  })

  it('explains inquiry history and lets staff assign a grade, section, and academic year', async () => {
    const user = userEvent.setup()
    const pendingInquiry: Inquiry = {
      ...inquiry,
      admission_for_class_id: null,
      status: 'PENDING',
      status_timeline: [{
        id: 21,
        from_status: null,
        to_status: 'PENDING',
        change_reason: 'Inquiry submitted via public form',
        created_at: '2026-11-11T10:11:15Z',
      }],
    }
    vi.spyOn(admissionsApi.inquiries, 'list').mockResolvedValue({
      items: [pendingInquiry],
      pagination: { page: 1, limit: 10, total_records: 1, total_pages: 1 },
    })
    vi.spyOn(admissionsApi.inquiries, 'get').mockResolvedValue(pendingInquiry)
    const updateStaff = vi.spyOn(admissionsApi.inquiries, 'updateStaff').mockResolvedValue(pendingInquiry)
    vi.spyOn(schoolApi.classes, 'list').mockResolvedValue({
      items: [
        { id: 23, class_teacher_id: null, name: '5th Grade', section: 'B', academic_year: '2026-2027', capacity: 40, status: 'active' },
      ],
      pagination: { page: 1, limit: 100, total_records: 1, total_pages: 1 },
    })
    renderWithAuth(<InquiriesPage />, ['inquiries.read', 'inquiries.review', 'classes.read'])

    await user.click(await screen.findByRole('button', { name: 'Details' }))
    expect(await screen.findByText(
      (_, element) => element?.tagName === 'STRONG' && element.textContent === 'Inquiry received → Pending review',
    )).toBeInTheDocument()
    expect(screen.getByText('Waiting for a staff member to begin reviewing this inquiry.')).toBeInTheDocument()
    expect(screen.getByText('Inquiry submitted via public form')).toBeInTheDocument()
    await user.selectOptions(screen.getByRole('combobox', { name: 'Grade level' }), '5th Grade')
    await user.selectOptions(screen.getByRole('combobox', { name: 'Section' }), 'B')
    await user.selectOptions(screen.getByRole('combobox', { name: 'Academic year' }), '2026-2027')
    await user.click(screen.getByRole('button', { name: 'Save notes and class' }))

    await waitFor(() => expect(updateStaff).toHaveBeenCalledWith(pendingInquiry.id, {
      admission_for_class_id: 23,
      internal_notes: '',
    }))
  })

  it('records a result only for an interview returned as scheduled', async () => {
    const user = userEvent.setup()
    vi.spyOn(admissionsApi.inquiries, 'list').mockResolvedValue({
      items: [inquiry],
      pagination: { page: 1, limit: 10, total_records: 1, total_pages: 1 },
    })
    vi.spyOn(admissionsApi.inquiries, 'get').mockResolvedValue(inquiry)
    vi.spyOn(admissionsApi.interviews, 'listForInquiry').mockResolvedValue([interview])
    const recordResult = vi.spyOn(admissionsApi.interviews, 'recordResult').mockResolvedValue({
      ...interview,
      result: 'FAILED',
    })
    renderWithAuth(<InterviewsPage />, ['inquiries.read', 'interviews.read', 'interviews.update'])

    await user.click(await screen.findByRole('button', { name: 'View interviews' }))
    await screen.findByText(/Result: SCHEDULED/)
    await user.click(screen.getByRole('button', { name: 'Record result' }))
    await user.selectOptions(screen.getByLabelText('Result'), 'FAILED')
    await user.click(screen.getByRole('button', { name: 'Save result' }))

    await waitFor(() => expect(recordResult).toHaveBeenCalledWith(interview.id, 'FAILED', undefined))
  })

  it('lets staff view a parent-uploaded document without exposing staff upload controls', async () => {
    const required = [
      'progress_report',
      'transfer_certificate',
      'student_aadhar',
      'parent_aadhar',
    ] as const
    vi.spyOn(admissionsApi.admissions, 'requiredDocuments').mockResolvedValue({ required: [...required] })
    const view = vi.spyOn(admissionsApi.admissions, 'viewDocument').mockResolvedValue(
      new Blob(['document'], { type: 'application/pdf' }),
    )
    const document = {
      id: 33,
      admission_id: 12,
      document_type: 'progress_report',
      file_name: 'report.pdf',
      verification_status: 'PENDING' as const,
      rejection_reason: null,
      verified_at: null,
    }
    const admission: Admission = {
      id: 12,
      admission_code: 'ADM202600012',
      inquiry_id: inquiry.id,
      class_id: 2,
      section: 'A',
      academic_year: '2026-2027',
      status: 'submitted',
      permanent_address: null,
      temporary_address: null,
      nationality: null,
      disability: null,
      blood_group: null,
      reason_for_school_change: null,
      rejection_reason: null,
      notes: null,
      student_id: null,
      documents: [document],
    }
    renderWithAuth(<AdmissionDocumentsPanel admission={admission} />, ['admissions.read'])

    await screen.findByText(/report.pdf/)
    expect(await screen.findByText('Migration certificate')).toBeInTheDocument()
    expect(screen.getByText('Character certificate')).toBeInTheDocument()
    expect(screen.getAllByText('Not uploaded (optional)')).toHaveLength(2)
    expect(screen.queryByRole('button', { name: 'Upload document' })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'View' }))

    await waitFor(() => expect(view).toHaveBeenCalledWith(document.id))
    expect(await screen.findByTitle('Preview report.pdf')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Zoom in' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Zoom out' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Fullscreen' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Download' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Print' })).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Zoom in' }))
    expect(screen.getByText('125%')).toBeInTheDocument()
  })
})
