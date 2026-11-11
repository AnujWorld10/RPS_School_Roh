import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from '@/App'
import { AuthContext, type AuthContextValue } from '@/features/auth/auth-context'
import { admissionsApi, type PublicInquiryStatus } from '@/features/admissions/admissions-api'
import { rolePortalApi, type SchoolEvent } from '@/features/school/role-portal-api'

const publicStatus: PublicInquiryStatus = {
  inquiry_code: 'INQ202600010',
  status: 'INTERVIEW_PASS',
  rejection_reason: null,
  admission_for_class: 'Grade 5',
  created_at: '2026-11-06T09:00:00Z',
  updated_at: null,
  status_timeline: [],
  latest_interview: null,
  admission: null,
}

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

function renderPortal(path: string) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[path]}>
        <AuthContext.Provider value={unauthenticatedContext}>
          <App />
        </AuthContext.Provider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

afterEach(() => {
  vi.restoreAllMocks()
})

describe('public parent admission portal', () => {
  it('shows only the requested public admission actions and supported staff login', async () => {
    renderPortal('/apply')

    expect(await screen.findByRole('heading', { name: 'Start an admission inquiry' })).toBeInTheDocument()
    expect(screen.getByRole('region', { name: 'Start an admission inquiry' })).toBeInTheDocument()
    expect(screen.getByRole('complementary')).toHaveTextContent('Admission inquiry')
    const services = screen.getByRole('navigation', { name: 'Admission services' })
    await userEvent.setup().click(within(services).getByRole('button', { name: 'Inquiry' }))
    expect(within(services).getByRole('link', { name: 'New inquiry' })).toHaveAttribute('href', '/apply')
    expect(within(services).getByRole('link', { name: 'Check inquiry status' })).toHaveAttribute(
      'href',
      '/application/status',
    )
    expect(within(services).getByRole('link', { name: 'Update inquiry details' })).toHaveAttribute(
      'href',
      '/application/update',
    )
    expect(within(services).getByRole('link', { name: 'Student Admission' })).toHaveAttribute(
      'href',
      '/application/submit',
    )
    await userEvent.setup().click(within(services).getByRole('button', { name: 'Sign in' }))
    expect(within(services).getByRole('link', { name: 'Staff Login' })).toHaveAttribute('href', '/login')
    expect(within(services).queryByRole('link', { name: 'Check status' })).not.toBeInTheDocument()
    expect(within(services).queryByRole('link', { name: 'Update inquiry' })).not.toBeInTheDocument()
    expect(screen.getByRole('navigation', { name: 'School website' })).toBeInTheDocument()
  })

  it('shows school location, academic stages, sample alumni, and the requested FAQs on the home page', async () => {
    renderPortal('/school/home')

    expect(await screen.findByRole('heading', { name: 'A pathway for every stage' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Primary' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Senior Secondary' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Frequently Asked Questions' })).toBeInTheDocument()
    expect(screen.getByText('When was the school established?')).toBeInTheDocument()
    expect(screen.getByText('What sporting activities does the school offer?')).toBeInTheDocument()
    expect(screen.getAllByText('Sample profile')).toHaveLength(3)

    const schoolNavigation = screen.getByRole('navigation', { name: 'School website' })
    await userEvent.setup().click(within(schoolNavigation).getByRole('button', { name: 'Inquiry' }))
    expect(within(schoolNavigation).getByRole('link', { name: 'New inquiry' })).toHaveAttribute('href', '/apply')
    expect(within(schoolNavigation).getByRole('link', { name: 'Check inquiry status' })).toHaveAttribute(
      'href',
      '/application/status',
    )
    expect(within(schoolNavigation).getByRole('link', { name: 'Update inquiry details' })).toHaveAttribute(
      'href',
      '/application/update',
    )

    const directions = screen.getByRole('link', { name: 'Open directions' })
    expect(directions).toHaveAttribute('href', 'https://maps.app.goo.gl/TwzsvhhR1TEu3HBN6')
    expect(directions).toHaveAttribute('target', '_blank')
  })

  it('provides school navigation and stage-specific academic information', async () => {
    const user = userEvent.setup()
    renderPortal('/school/about/about-rps')

    expect(await screen.findByRole('heading', { name: 'About RPS' })).toBeInTheDocument()
    expect(screen.getByText('Sample website content — please have the school review and approve this information before publication.')).toBeInTheDocument()
    const schoolNavigation = screen.getByRole('navigation', { name: 'School website' })
    const academics = within(schoolNavigation).getByRole('button', { name: 'Academics' })
    await user.click(academics)
    expect(academics).toHaveAttribute('aria-expanded', 'true')
    await user.click(screen.getByRole('heading', { name: 'About RPS' }))
    expect(academics).toHaveAttribute('aria-expanded', 'false')
    await user.click(academics)
    await user.keyboard('{Escape}')
    expect(academics).toHaveAttribute('aria-expanded', 'false')
    await user.click(academics)

    await user.click(screen.getByRole('link', { name: 'Primary (Class I–V)' }))

    expect(await screen.findByRole('heading', { name: 'Primary (Class I–V)' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Primary (Class I–V)' })).toHaveAttribute('aria-current', 'page')
    expect(within(screen.getByRole('navigation', { name: 'School website' })).getByRole('button', { name: 'Academics' })).toHaveAttribute(
      'aria-expanded',
      'false',
    )
    expect(screen.getByRole('heading', { name: 'Learning goals for this stage' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Strong foundations' })).toBeInTheDocument()
    expect(screen.getByText(/Illustrative programme overview/)).toBeInTheDocument()
    expect(schoolNavigation).toBeInTheDocument()
  })

  it('renders professional sample content for all six About pages', async () => {
    const aboutSamples = [
      ['/school/about/about-rps', 'About RPS', 'A place to learn and grow'],
      ['/school/about/chairmans-message', "Chairman's Message", 'A message from our leadership'],
      ['/school/about/principals-message', "Principal's Message", 'A message from our Principal'],
      ['/school/about/vision-mission', 'Vision & Mission', 'What guides us'],
      ['/school/about/infrastructure', 'Infrastructure', 'Spaces that support learning'],
      ['/school/about/teachers', 'Teachers', 'The people who support learning'],
    ] as const

    for (const [path, title, eyebrow] of aboutSamples) {
      const { unmount } = renderPortal(path)
      expect(await screen.findByRole('heading', { name: title })).toBeInTheDocument()
      expect(screen.getByText(eyebrow)).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: 'Our approach' })).toBeInTheDocument()
      expect(screen.getByText(/Sample website content/)).toBeInTheDocument()
      unmount()
    }
  })

  it('renders a structured academic programme for every school stage', async () => {
    const academicStages = [
      ['/school/academics/primary', 'Primary (Class I–V)', 'Strong foundations'],
      ['/school/academics/middle', 'Middle School (Class VI–VIII)', 'Deeper understanding'],
      ['/school/academics/secondary', 'Secondary (Class IX–X)', 'Subject mastery'],
      ['/school/academics/senior', 'Senior Secondary (Class XI–XII)', 'Advanced learning'],
    ] as const

    for (const [path, title, goal] of academicStages) {
      const { unmount } = renderPortal(path)
      expect(await screen.findByRole('heading', { name: title })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: 'Learning goals for this stage' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: goal })).toBeInTheDocument()
      expect(screen.getByRole('navigation', { name: 'Academic stages' })).toBeInTheDocument()
      expect(screen.getByText(/Illustrative programme overview/)).toBeInTheDocument()
      unmount()
    }
  })

  it('provides a public Careers page without inventing vacancy details', async () => {
    renderPortal('/school/careers')

    expect(await screen.findByRole('heading', { name: 'Careers' })).toBeInTheDocument()
    expect(screen.getByText(/Verified school information for this section has not been added yet/)).toBeInTheDocument()
    expect(screen.getByRole('navigation', { name: 'School website' })).toBeInTheDocument()
  })

  it('shows a structured Contact page and clearly labels placeholder details', async () => {
    renderPortal('/school/contact')

    expect(await screen.findByRole('heading', { name: 'Contact RPS School' })).toBeInTheDocument()
    expect(screen.getByText(/Demo content only/)).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Visit the school' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Call the office' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Find our campus' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'View location' })).toHaveAttribute(
      'href',
      'https://maps.app.goo.gl/TwzsvhhR1TEu3HBN6',
    )
    expect(screen.getByRole('link', { name: 'Start an inquiry' })).toHaveAttribute('href', '/apply')
  })

  it('renders searchable and filterable notices without inventing unpublished school notices', async () => {
    const user = userEvent.setup()
    renderPortal('/school/notices')

    expect(await screen.findByRole('heading', { name: 'School Notices' })).toBeInTheDocument()
    expect(screen.getByRole('searchbox', { name: 'Search notices' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'No notices published yet' })).toBeInTheDocument()
    expect(screen.getByText('Showing 0 of 0 notices')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'EXAMINATION' }))
    expect(screen.getByRole('button', { name: 'EXAMINATION' })).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByRole('heading', { name: 'No matching notices' })).toBeInTheDocument()
  })

  it('shows the school images supplied for the public gallery', async () => {
    renderPortal('/school/gallery')

    expect(await screen.findByRole('heading', { name: 'School Gallery' })).toBeInTheDocument()
    expect(screen.getAllByRole('img')).toHaveLength(4)
  })

  it('loads published public school events without requiring sign in', async () => {
    const publicEvent: SchoolEvent = {
      id: 1,
      title: 'School Open Day',
      description: 'Meet our teachers and explore the campus.',
      starts_at: '2026-12-01T09:00:00Z',
      ends_at: '2026-12-01T12:00:00Z',
      venue: 'Main campus',
      audience: 'public',
      status: 'published',
      created_by: 1,
      reviewed_by: 2,
      rejection_reason: null,
    }
    const fetchEvents = vi.spyOn(rolePortalApi, 'publicEvents').mockResolvedValue([publicEvent])
    renderPortal('/school/events')

    expect(await screen.findByRole('heading', { name: 'School Open Day' })).toBeInTheDocument()
    expect(screen.getByText('Meet our teachers and explore the campus.')).toBeInTheDocument()
    expect(fetchEvents).toHaveBeenCalledOnce()
  })

  it('replaces the inquiry form with a confirmation and lets the user start a new inquiry', async () => {
    const user = userEvent.setup()
    const createInquiry = vi.spyOn(admissionsApi.public, 'createInquiry').mockResolvedValue({
      inquiry_code: 'INQ202600010',
      status: 'PENDING',
      message: 'Inquiry submitted successfully.',
    })
    renderPortal('/apply')

    await screen.findByRole('heading', { name: 'Start an admission inquiry' })
    await user.type(screen.getByLabelText(/Student first name/), 'Taylor')
    await user.type(screen.getByLabelText(/Student middle name/), 'A')
    await user.type(screen.getByLabelText(/Student last name/), 'Example')
    await user.selectOptions(screen.getByLabelText(/Gender/), 'female')
    await user.type(screen.getByLabelText(/Parent or guardian name/), 'Morgan Example')
    fireEvent.change(screen.getByLabelText(/Date of birth/), { target: { value: '2016-03-12' } })
    await user.type(screen.getByLabelText(/Parent mobile/), '+15555550112')
    await user.type(screen.getByLabelText(/Student mobile/), '+15555550113')
    await user.type(screen.getByLabelText(/Parent email/), 'parent@example.com')
    await user.type(screen.getByLabelText(/Residential address/), '12 North School Road')
    await user.type(screen.getByLabelText(/Last school attended/), 'Example Primary')
    await user.type(screen.getByLabelText(/Current class or grade/), 'Grade 4')
    await user.type(screen.getByLabelText(/Requested class or grade/), 'Grade 5')
    await user.click(screen.getByRole('button', { name: 'Submit inquiry' }))

    expect(await screen.findByRole('heading', { name: 'Inquiry submitted successfully' })).toBeInTheDocument()
    expect(screen.getByText('INQ202600010')).toBeInTheDocument()
    expect(screen.queryByRole('textbox', { name: /Student first name/ })).not.toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Check your status' })).toHaveAttribute('href', '/application/status')
    expect(screen.getByRole('link', { name: '+91 8967558216' })).toHaveAttribute('href', 'tel:+918967558216')
    expect(screen.getByRole('link', { name: 'rpsschoolroh@gmail.com' })).toHaveAttribute('href', 'mailto:rpsschoolroh@gmail.com')
    expect(createInquiry).toHaveBeenCalledWith(expect.objectContaining({
      first_name: 'Taylor',
      last_name: 'Example',
      email: 'parent@example.com',
      parent_mobile: '+15555550112',
      admission_for_class: 'Grade 5',
    }))

    await user.click(screen.getByRole('button', { name: 'Apply new inquiry' }))
    expect(await screen.findByRole('heading', { name: 'Start an admission inquiry' })).toBeInTheDocument()
    expect(screen.getByRole('textbox', { name: /Student first name/ })).toHaveValue('')
    expect(screen.queryByRole('heading', { name: 'Inquiry submitted successfully' })).not.toBeInTheDocument()
  })

  it('checks status using the inquiry code and parent verification details', async () => {
    const user = userEvent.setup()
    const getStatus = vi.spyOn(admissionsApi.public, 'getInquiryStatus').mockResolvedValue(publicStatus)
    renderPortal('/application/status')

    expect(await screen.findByRole('heading', { name: 'Check inquiry status' })).toBeInTheDocument()
    await user.type(screen.getByLabelText(/Inquiry code/), 'INQ202600010')
    await user.type(screen.getByLabelText(/Parent email/), 'parent@example.com')
    await user.type(screen.getByLabelText(/Parent mobile/), '+15555550112')
    await user.click(screen.getByRole('button', { name: 'Check status' }))

    expect(getStatus).toHaveBeenCalled()
    expect(await screen.findByText('Inquiry INQ202600010')).toBeInTheDocument()
    expect(getStatus).toHaveBeenCalledWith('INQ202600010', 'parent@example.com', '+15555550112')
    expect(screen.getByRole('link', { name: 'Continue to admission application' })).toHaveAttribute('href', '/application/submit')
  })

  it('shows the enrolled student ID and downloads a credential-verified admission letter', async () => {
    const user = userEvent.setup()
    const enrolledStatus: PublicInquiryStatus = {
      ...publicStatus,
      status: 'ADMISSION_SUCCESS',
      admission: {
        admission_code: 'RPS00001',
        status: 'approved',
        documents_uploaded: 6,
        documents_required: 6,
        documents: [],
        student_code: 'RPS00001',
        student_name: 'Taylor Example',
        class_name: 'Grade 5',
        section: 'A',
        academic_year: '2026-2027',
        roll_number: 14,
      },
    }
    vi.spyOn(admissionsApi.public, 'getInquiryStatus').mockResolvedValue(enrolledStatus)
    const downloadLetter = vi.spyOn(admissionsApi.public, 'downloadAdmissionLetter')
      .mockResolvedValue(new Blob(['%PDF']))
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined)
    renderPortal('/application/status')

    await user.type(await screen.findByLabelText(/Inquiry code/), 'INQ202600010')
    await user.type(screen.getByLabelText(/Parent email/), 'parent@example.com')
    await user.type(screen.getByLabelText(/Parent mobile/), '+15555550112')
    await user.click(screen.getByRole('button', { name: 'Check status' }))

    expect(await screen.findByText('RPS00001')).toBeInTheDocument()
    expect(screen.getByText(/Taylor Example has been admitted to Grade 5/)).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Download admission letter (PDF)' }))
    await waitFor(() => {
      expect(downloadLetter).toHaveBeenCalledWith(
        'INQ202600010',
        'parent@example.com',
        '+15555550112',
      )
    })
  })

  it('updates inquiry details using public parent verification', async () => {
    const user = userEvent.setup()
    const updateInquiry = vi.spyOn(admissionsApi.public, 'updateInquiry').mockResolvedValue(publicStatus)
    renderPortal('/application/update')

    expect(await screen.findByRole('heading', { name: 'Update inquiry details' })).toBeInTheDocument()
    await user.type(screen.getByLabelText(/Inquiry code/), 'INQ202600010')
    await user.type(screen.getByLabelText(/Parent email/), 'parent@example.com')
    await user.type(screen.getByLabelText(/Parent mobile/), '+15555550112')
    await user.type(screen.getByLabelText(/Student first name/), 'Taylor')
    await user.click(screen.getByRole('button', { name: 'Update inquiry' }))

    expect(await screen.findByRole('heading', { name: 'Inquiry details updated' })).toBeInTheDocument()
    expect(screen.getByText('INQ202600010')).toBeInTheDocument()
    expect(screen.getByText(/Your requested changes have been submitted successfully/)).toBeInTheDocument()
    expect(screen.getByText('Student first name')).toBeInTheDocument()
    expect(screen.queryByRole('textbox', { name: /Parent email/ })).not.toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Check your status' })).toHaveAttribute('href', '/application/status')
    expect(screen.getByRole('link', { name: 'Apply new inquiry' })).toHaveAttribute('href', '/apply')
    expect(screen.getByRole('link', { name: '+91 8967558216' })).toHaveAttribute('href', 'tel:+918967558216')
    expect(screen.getByRole('link', { name: 'rpsschoolroh@gmail.com' })).toHaveAttribute('href', 'mailto:rpsschoolroh@gmail.com')
    expect(updateInquiry).toHaveBeenCalledWith(expect.objectContaining({
      inquiry_code: 'INQ202600010',
      email: 'parent@example.com',
      parent_mobile: '+15555550112',
      first_name: 'Taylor',
    }))

    await user.click(screen.getByRole('link', { name: 'Apply new inquiry' }))
    expect(await screen.findByRole('heading', { name: 'Start an admission inquiry' })).toBeInTheDocument()
    expect(screen.getByRole('textbox', { name: /Student first name/ })).toBeInTheDocument()
  })

  it('submits admission only with the public API class ID and parent credentials', async () => {
    const user = userEvent.setup()
    const listAdmissionClasses = vi.spyOn(admissionsApi.public, 'listAdmissionClasses').mockResolvedValue([
      { id: 7, name: 'Grade 5', section: 'A', academic_year: '2026-2027' },
      { id: 8, name: 'Grade 6', section: null, academic_year: '2026-2027' },
      { id: 9, name: 'Grade 4', section: 'A', academic_year: '2025-26' },
    ])
    const getInquiryStatus = vi.spyOn(admissionsApi.public, 'getInquiryStatus').mockResolvedValue(publicStatus)
    const submitAdmission = vi.spyOn(admissionsApi.public, 'submitAdmission').mockResolvedValue({
      admission_code: 'ADM202600010',
      status: 'submitted',
    })
    vi.spyOn(admissionsApi.public, 'uploadAdmissionDocument').mockResolvedValue({
      document_type: 'progress_report',
      verification_status: 'PENDING',
      rejection_reason: null,
      verified_at: null,
    })
    const { container } = renderPortal('/application/submit')

    expect(await screen.findByRole('heading', { name: 'Submit admission application' })).toBeInTheDocument()
    await user.type(screen.getByLabelText(/Inquiry code/), 'INQ202600010')
    await user.type(screen.getByLabelText(/Parent email/), 'parent@example.com')
    await user.type(screen.getByLabelText(/Parent mobile/), '+15555550112')
    await user.click(screen.getByRole('button', { name: 'Verify inquiry' }))

    expect(await screen.findByText(/Current status: INTERVIEW_PASS/)).toBeInTheDocument()
    expect(listAdmissionClasses).toHaveBeenCalled()
    const classSelect = await screen.findByLabelText(/Class and academic year/)
    expect(classSelect).toHaveValue('7')
    expect(within(classSelect).getByRole('option', {
      name: 'Grade 6 · 2026-2027',
    })).toBeInTheDocument()
    expect(within(classSelect).getByRole('option', {
      name: 'Grade 4 — Section A · 2025-26',
    })).toBeInTheDocument()
    await user.type(screen.getByLabelText(/Student Aadhaar number/), '123456789012')
    await user.type(screen.getByLabelText(/Parent \/ guardian Aadhaar number/), '987654321098')
    await user.type(screen.getByLabelText(/Marks obtained at last school/), '450')
    await user.type(screen.getByLabelText(/Last-school percentage/), '90')
    await user.type(screen.getByLabelText(/Last-school student ID \/ roll number/), 'ROLL-12')
    for (const index of [0, 1, 2, 3, 4, 5]) {
      const file = new File([`file-${index}`], `${index}.pdf`, { type: 'application/pdf' })
      const fileInput = container.querySelectorAll<HTMLInputElement>('input[type="file"]')[index]
      fireEvent.change(fileInput, { target: { files: [file] } })
    }
    await user.click(screen.getByRole('button', { name: 'Submit admission application' }))

    expect(await screen.findByText('Admission application submitted')).toBeInTheDocument()
    expect(submitAdmission).toHaveBeenCalledWith(expect.objectContaining({
      inquiry_code: 'INQ202600010',
      email: 'parent@example.com',
      parent_mobile: '+15555550112',
      class_id: 7,
      academic_year: '2026-2027',
    }))
    expect(getInquiryStatus).toHaveBeenCalledWith('INQ202600010', 'parent@example.com', '+15555550112')
    expect(listAdmissionClasses).toHaveBeenCalled()
  })

  it('does not show class selection until the school records an interview pass', async () => {
    const user = userEvent.setup()
    const pendingInquiry = { ...publicStatus, status: 'PENDING' }
    const getInquiryStatus = vi.spyOn(admissionsApi.public, 'getInquiryStatus')
      .mockResolvedValue(pendingInquiry)
    const listAdmissionClasses = vi.spyOn(admissionsApi.public, 'listAdmissionClasses')
      .mockResolvedValue([{ id: 7, name: 'Grade 5', section: 'A', academic_year: '2026-2027' }])
    renderPortal('/application/submit')

    await user.type(await screen.findByLabelText(/Inquiry code/), 'INQ202600010')
    await user.type(screen.getByLabelText(/Parent email/), 'parent@example.com')
    await user.type(screen.getByLabelText(/Parent mobile/), '+15555550112')
    await user.click(screen.getByRole('button', { name: 'Verify inquiry' }))

    expect(await screen.findByText('Admission application is not ready yet')).toBeInTheDocument()
    expect(screen.queryByLabelText(/Academic year/)).not.toBeInTheDocument()
    expect(getInquiryStatus).toHaveBeenCalled()
    expect(listAdmissionClasses).not.toHaveBeenCalled()
  })
})
