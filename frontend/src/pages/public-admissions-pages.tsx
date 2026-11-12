import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { CheckCircle2, GraduationCap, Mail, Phone } from 'lucide-react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'
import { z } from 'zod'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ErrorState, SuccessState } from '@/components/ui/async-state'
import { FormField } from '@/components/ui/form-field'
import { Input } from '@/components/ui/input'
import { PageHeader } from '@/components/ui/page-header'
import { PublicSchoolNavigation } from '@/components/layout/public-school-navigation'
import { PublicNavDropdown } from '@/components/layout/public-nav-dropdown'
import {
  admissionsApi,
  OPTIONAL_ADMISSION_DOCUMENT_TYPES,
  REQUIRED_ADMISSION_DOCUMENT_TYPES,
  type DocumentType,
  type PublicInquiryStatus,
} from '@/features/admissions/admissions-api'
import { toApiError } from '@/lib/api/api-error'

function PublicPortalLayout() {
  const navClass = ({ isActive }: { isActive: boolean }) =>
    `rounded-md px-3 py-2 text-sm font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-300 ${
      isActive ? 'bg-white/15 text-white' : 'text-slate-200 hover:bg-white/10 hover:text-white'
    }`

  return (
    <div className="public-portal min-h-screen text-slate-950">
      <header className="border-b border-border bg-background">
        <div className="bg-slate-900">
          <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-4 sm:px-6 md:flex-row md:items-center md:justify-between">
          <Link className="flex items-center gap-3 font-semibold text-white" to="/apply">
            <span className="flex size-10 items-center justify-center rounded-xl bg-amber-400 text-slate-950 shadow-md shadow-black/20">
              <GraduationCap aria-hidden="true" size={22} />
            </span>
            <span className="tracking-tight">RPS School <span className="font-normal text-teal-200">· Parent portal</span></span>
          </Link>
          <nav aria-label="Admission services" className="flex flex-wrap items-center gap-1">
            <PublicNavDropdown
              items={[
                { label: 'New inquiry', to: '/apply' },
                { label: 'Check inquiry status', to: '/application/status' },
                { label: 'Update inquiry details', to: '/application/update' },
              ]}
              label="Inquiry"
              triggerClassName={navClass({ isActive: false })}
            />
            <NavLink className={navClass} to="/application/submit">Student Admission</NavLink>
            <PublicNavDropdown
              align="right"
              items={[
                { label: 'Student Login', to: '/login?portal=student' },
                { label: 'Parent Login', to: '/login?portal=parent' },
                { label: 'Teacher Login', to: '/login?portal=teacher' },
                { label: 'Administration Login', to: '/login?portal=administration' },
                { label: 'Staff Login', to: '/login' },
              ]}
              label="Sign in"
              triggerClassName="text-slate-200 hover:bg-white/10 hover:text-white focus-visible:outline-teal-300"
            />
          </nav>
          </div>
        </div>
        <div className="mx-auto max-w-6xl px-4 py-2 sm:px-6">
          <PublicSchoolNavigation showInquiryMenu={false} />
        </div>
      </header>
      <main className="mx-auto grid w-full max-w-6xl gap-6 px-4 py-8 sm:px-6 sm:py-10">
        <Outlet />
      </main>
      <footer className="border-t border-border bg-white px-4 py-5 text-center text-xs text-muted-foreground">
        RPS School Management · Parent admission services
      </footer>
    </div>
  )
}

const inquirySchema = z.object({
  first_name: z.string().trim().min(1, 'Enter the student first name.').max(100),
  middle_name: z.string().trim().max(100).optional(),
  last_name: z.string().trim().min(1, 'Enter the student last name.').max(100),
  gender: z.enum(['male', 'female', 'other']),
  father_name: z.string().trim().min(1, 'Enter a parent or guardian name.').max(200),
  dob: z.iso.date().refine((value) => value <= new Date().toISOString().slice(0, 10), 'Date of birth cannot be in the future.'),
  student_mobile: z.string().trim().max(30).optional(),
  parent_mobile: z.string().trim().min(5, 'Enter a valid parent mobile number.').max(30),
  email: z.string().trim().email('Enter a valid parent email address.'),
  address: z.string().trim().min(5, 'Enter an address of at least 5 characters.'),
  last_school: z.string().trim().min(1, 'Enter the last school attended.').max(255),
  current_class: z.string().trim().min(1, 'Enter the current class or grade.').max(100),
  admission_for_class: z.string().trim().min(1, 'Enter the requested class or grade.').max(100),
})

type InquiryValues = z.infer<typeof inquirySchema>

const initialInquiryValues: InquiryValues = {
  first_name: '',
  middle_name: '',
  last_name: '',
  gender: 'male',
  father_name: '',
  dob: '',
  student_mobile: '',
  parent_mobile: '',
  email: '',
  address: '',
  last_school: '',
  current_class: '',
  admission_for_class: '',
}

export function PublicInquiryPage() {
  const form = useForm<InquiryValues>({
    resolver: zodResolver(inquirySchema),
    defaultValues: initialInquiryValues,
  })
  const mutation = useMutation({
    mutationFn: (values: InquiryValues) => admissionsApi.public.createInquiry({
      ...values,
      middle_name: values.middle_name || null,
      student_mobile: values.student_mobile || null,
    }),
    onSuccess: () => form.reset(initialInquiryValues),
  })
  const error = mutation.error ? toApiError(mutation.error) : null

  return (
    <div className="grid w-full gap-8 lg:grid-cols-[minmax(0,36rem)_minmax(16rem,1fr)] lg:items-start">
      <section aria-label={mutation.data ? 'Inquiry submitted' : 'Start an admission inquiry'} className="min-w-0">
        {mutation.data ? (
          <div aria-labelledby="inquiry-confirmation-title" className="rounded-2xl border border-emerald-200 bg-white p-6 shadow-lg shadow-emerald-950/5 sm:p-8" role="status">
            <span className="flex size-12 items-center justify-center rounded-full bg-emerald-100 text-emerald-700">
              <CheckCircle2 aria-hidden="true" size={26} />
            </span>
            <h1 className="mt-4 text-2xl font-semibold tracking-tight text-slate-950" id="inquiry-confirmation-title">
              Inquiry submitted successfully
            </h1>
            <p className="mt-2 text-sm leading-6 text-slate-600">{mutation.data.message}</p>
            <div className="mt-6 rounded-xl border border-teal-200 bg-teal-50 p-4 sm:p-5">
              <p className="text-sm font-semibold text-teal-950">Your inquiry ID</p>
              <p className="mt-1 break-all font-mono text-2xl font-bold tracking-wide text-teal-900 sm:text-3xl">
                {mutation.data.inquiry_code}
              </p>
              <p className="mt-2 text-sm leading-6 text-teal-900">
                Please save this ID. You will need it with your parent email and mobile number to check your status or make allowed updates.
              </p>
            </div>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link
                className="inline-flex h-9 items-center justify-center rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/80 focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
                state={{ inquiryCode: mutation.data.inquiry_code }}
                to="/application/status"
              >
                Check your status
              </Link>
              <Button
                onClick={() => {
                  form.reset(initialInquiryValues)
                  mutation.reset()
                }}
                type="button"
                variant="outline"
              >
                Apply new inquiry
              </Button>
            </div>
            <div className="mt-7 border-t border-slate-200 pt-5">
              <p className="text-sm font-semibold text-slate-900">Need more information or have a question?</p>
              <p className="mt-1 text-sm leading-6 text-slate-600">Please contact our administrative team:</p>
              <div className="mt-3 flex flex-wrap gap-x-6 gap-y-2">
                <a className="inline-flex items-center gap-2 text-sm font-semibold text-teal-800 hover:text-teal-950" href="tel:+918967558216">
                  <Phone aria-hidden="true" className="size-4" />
                  +91 8967558216
                </a>
                <a className="inline-flex items-center gap-2 text-sm font-semibold text-teal-800 hover:text-teal-950" href="mailto:rpsschoolroh@gmail.com">
                  <Mail aria-hidden="true" className="size-4" />
                  rpsschoolroh@gmail.com
                </a>
              </div>
            </div>
          </div>
        ) : (
          <>
            <PageHeader
              title="Start an admission inquiry"
              description="Submit your child’s details without creating a school staff account. Save the inquiry code shown after submission."
            />
            {error ? (
              <div className="mb-5">
                <ErrorState
                  title={error.status === 409 ? 'Possible duplicate inquiry' : 'Inquiry submission failed'}
                  description={error.status === 409
                    ? `${error.message} Contact the school office if you believe this is a different applicant.`
                    : error.message}
                />
              </div>
            ) : null}
        <Card className="border border-border/80 bg-white shadow-lg shadow-slate-900/5">
          <CardHeader className="border-b border-teal-100 bg-gradient-to-r from-teal-50 to-white">
            <CardTitle>Student and parent details</CardTitle>
            <CardDescription>Required fields are marked. The backend validates every submission.</CardDescription>
          </CardHeader>
          <CardContent>
            <form
              className="grid gap-4 sm:grid-cols-2"
              noValidate
              onSubmit={form.handleSubmit((values) => mutation.mutate(values))}
            >
            <FormField error={form.formState.errors.first_name?.message} label="Student first name" required>
              {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('first_name')} />}
            </FormField>
            <FormField error={form.formState.errors.middle_name?.message} label="Student middle name">
              {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('middle_name')} />}
            </FormField>
            <FormField error={form.formState.errors.last_name?.message} label="Student last name" required>
              {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('last_name')} />}
            </FormField>
            <FormField error={form.formState.errors.gender?.message} label="Gender" required>
              {({ id, describedBy }) => (
                <select id={id} aria-describedby={describedBy} className="h-10 rounded-lg border border-input bg-white px-3 text-sm" {...form.register('gender')}>
                  <option value="male">Male</option><option value="female">Female</option><option value="other">Other</option>
                </select>
              )}
            </FormField>
            <FormField error={form.formState.errors.father_name?.message} label="Parent or guardian name" required>
              {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('father_name')} />}
            </FormField>
            <FormField error={form.formState.errors.dob?.message} label="Date of birth" required>
              {({ id, describedBy }) => <Input id={id} max={new Date().toISOString().slice(0, 10)} type="date" aria-describedby={describedBy} {...form.register('dob')} />}
            </FormField>
            <FormField error={form.formState.errors.parent_mobile?.message} label="Parent mobile" required description="Used with the inquiry code to verify access to this application.">
              {({ id, describedBy }) => <Input id={id} type="tel" autoComplete="tel" aria-describedby={describedBy} {...form.register('parent_mobile')} />}
            </FormField>
            <FormField error={form.formState.errors.student_mobile?.message} label="Student mobile">
              {({ id, describedBy }) => <Input id={id} type="tel" aria-describedby={describedBy} {...form.register('student_mobile')} />}
            </FormField>
            <FormField error={form.formState.errors.email?.message} label="Parent email" required description="Use this same email for status checks and updates.">
              {({ id, describedBy }) => <Input id={id} type="email" autoComplete="email" aria-describedby={describedBy} {...form.register('email')} />}
            </FormField>
            <FormField error={form.formState.errors.address?.message} label="Residential address" required>
              {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('address')} />}
            </FormField>
            <FormField error={form.formState.errors.last_school?.message} label="Last school attended" required>
              {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('last_school')} />}
            </FormField>
            <FormField error={form.formState.errors.current_class?.message} label="Current class or grade" required>
              {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('current_class')} />}
            </FormField>
            <FormField error={form.formState.errors.admission_for_class?.message} label="Requested class or grade" required>
              {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('admission_for_class')} />}
            </FormField>
            <div className="flex flex-wrap items-center gap-3 sm:col-span-2">
              <Button disabled={mutation.isPending} type="submit">
                {mutation.isPending ? 'Submitting inquiry…' : 'Submit inquiry'}
              </Button>
              <Link className="text-sm font-medium text-teal-800 underline-offset-4 hover:underline" to="/application/status">
                Already applied? Check your status
              </Link>
            </div>
            </form>
          </CardContent>
        </Card>
          </>
        )}
      </section>
      <aside className="hidden rounded-xl border border-teal-900/10 bg-gradient-to-br from-teal-900 to-slate-900 p-6 text-white shadow-xl shadow-teal-950/15 lg:block">
        <span className="inline-flex rounded-full bg-amber-300/15 px-3 py-1 text-xs font-semibold tracking-wide text-amber-200">ADMISSIONS</span>
        <h2 className="mt-4 text-lg font-semibold">Admission inquiry</h2>
        <p className="mt-2 text-sm leading-6 text-slate-200">
          You can submit an inquiry without a staff account. Keep the inquiry code and use the parent contact details provided here to verify access later.
        </p>
        <div className="mt-5 grid gap-3 border-t border-white/15 pt-4">
          <Link
            className="text-sm font-semibold text-amber-200 underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-300"
            to="/application/status"
          >
            Already applied? Check your status
          </Link>
          <Link
            className="text-sm font-semibold text-amber-200 underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-300"
            to="/application/update"
          >
            Update inquiry details
          </Link>
        </div>
      </aside>
    </div>
  )
}

const credentialsSchema = z.object({
  inquiry_code: z.string().trim().min(5).max(20),
  email: z.string().trim().email('Enter the email used on the inquiry.'),
  parent_mobile: z.string().trim().min(5).max(30),
})

type Credentials = z.infer<typeof credentialsSchema>

function InquiryCredentialsForm({
  onSubmit,
  isPending,
  buttonLabel,
  initialInquiryCode = '',
}: {
  onSubmit: (values: Credentials) => void
  isPending: boolean
  buttonLabel: string
  initialInquiryCode?: string
}) {
  const form = useForm<Credentials>({
    resolver: zodResolver(credentialsSchema),
    defaultValues: { inquiry_code: initialInquiryCode, email: '', parent_mobile: '' },
  })

  return (
    <form className="grid gap-4 sm:grid-cols-3" noValidate onSubmit={form.handleSubmit(onSubmit)}>
      <FormField error={form.formState.errors.inquiry_code?.message} label="Inquiry code" required description="Found on the inquiry submission confirmation.">
        {({ id, describedBy }) => <Input id={id} autoComplete="off" aria-describedby={describedBy} {...form.register('inquiry_code')} />}
      </FormField>
      <FormField error={form.formState.errors.email?.message} label="Parent email" required>
        {({ id, describedBy }) => <Input id={id} type="email" autoComplete="email" aria-describedby={describedBy} {...form.register('email')} />}
      </FormField>
      <FormField error={form.formState.errors.parent_mobile?.message} label="Parent mobile" required>
        {({ id, describedBy }) => <Input id={id} type="tel" autoComplete="tel" aria-describedby={describedBy} {...form.register('parent_mobile')} />}
      </FormField>
      <div className="sm:col-span-3">
        <Button disabled={isPending} type="submit">{isPending ? 'Checking…' : buttonLabel}</Button>
      </div>
    </form>
  )
}

const documentLabels: Record<DocumentType, string> = {
  progress_report: 'Progress report',
  transfer_certificate: 'Transfer certificate',
  migration_certificate: 'Migration certificate',
  character_certificate: 'Character certificate',
  student_aadhar: 'Student Aadhaar document',
  parent_aadhar: 'Parent Aadhaar document',
}

const requiredAdmissionDocuments = REQUIRED_ADMISSION_DOCUMENT_TYPES
const optionalAdmissionDocuments = OPTIONAL_ADMISSION_DOCUMENT_TYPES
const submissionDocumentTypes = [...requiredAdmissionDocuments, ...optionalAdmissionDocuments]

function PublicAdmissionDocumentUploads({
  credentials,
  documents,
  onUploaded,
}: {
  credentials: Credentials
  documents: NonNullable<PublicInquiryStatus['admission']>['documents']
  onUploaded: () => void
}) {
  const [files, setFiles] = useState<Partial<Record<DocumentType, File>>>({})
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const uploadMutation = useMutation({
    mutationFn: ({ type, file }: { type: DocumentType; file: File }) =>
      admissionsApi.public.uploadAdmissionDocument(credentials, type, file),
    onSuccess: (_, variables) => {
      setFiles((current) => {
        const next = { ...current }
        delete next[variables.type]
        return next
      })
      setErrorMessage(null)
      onUploaded()
    },
    onError: (error) => setErrorMessage(toApiError(error).message),
  })
  const documentsByType = new Map((documents ?? []).map((document) => [document.document_type, document]))
  const needsUpload = requiredAdmissionDocuments.filter((type) => {
    const document = documentsByType.get(type)
    return !document || document.verification_status === 'REJECTED'
  }).concat(optionalAdmissionDocuments.filter((type) => {
    const document = documentsByType.get(type)
    return !document || document.verification_status === 'REJECTED'
  }))

  if (!needsUpload.length) return null

  return (
    <section className="grid gap-3">
      <h3 className="font-semibold">Upload missing or rejected documents</h3>
      {errorMessage ? <ErrorState title="Document upload failed" description={errorMessage} /> : null}
      <div className="grid gap-3 sm:grid-cols-2">
        {needsUpload.map((type) => (
          <div className="grid gap-2 rounded-lg border p-3" key={type}>
            <label className="text-sm font-medium" htmlFor={`status-document-${type}`}>{documentLabels[type]}</label>
            <input
              accept=".pdf,.jpg,.jpeg,.png"
              className="block w-full text-sm"
              id={`status-document-${type}`}
              onChange={(event) => {
                const file = event.currentTarget.files?.[0]
                if (file) setFiles((current) => ({ ...current, [type]: file }))
              }}
              type="file"
            />
            <Button
              disabled={!files[type] || uploadMutation.isPending}
              onClick={() => {
                const file = files[type]
                if (file) uploadMutation.mutate({ type, file })
              }}
              size="sm"
              type="button"
            >
              {uploadMutation.isPending ? 'Uploading…' : 'Upload document'}
            </Button>
          </div>
        ))}
      </div>
      <p className="text-xs text-slate-500">PDF, JPG, JPEG, or PNG files up to the configured upload limit are accepted.</p>
    </section>
  )
}

function InquiryProgress({
  status,
  credentials,
  onRefresh,
}: {
  status: PublicInquiryStatus
  credentials: Credentials
  onRefresh: () => void
}) {
  const [letterError, setLetterError] = useState<string | null>(null)
  const letterMutation = useMutation({
    mutationFn: () => admissionsApi.public.downloadAdmissionLetter(
      credentials.inquiry_code,
      credentials.email,
      credentials.parent_mobile,
    ),
    onSuccess: (blob) => {
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${status.admission?.student_code ?? 'RPS'}-admission.pdf`
      link.click()
      window.setTimeout(() => URL.revokeObjectURL(url), 1000)
      setLetterError(null)
    },
    onError: (error) => setLetterError(toApiError(error).message),
  })
  return (
    <Card>
      <CardHeader>
        <CardTitle>Inquiry {status.inquiry_code}</CardTitle>
        <CardDescription>Current status: <strong>{status.status}</strong> · Requested class: {status.admission_for_class}</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-6">
        {status.rejection_reason ? (
          <Alert variant="destructive"><AlertTitle>Application update</AlertTitle><AlertDescription>{status.rejection_reason}</AlertDescription></Alert>
        ) : null}
        {status.latest_interview ? (
          <section className="grid gap-1 text-sm">
            <h2 className="font-semibold">Latest interview</h2>
            <p>{status.latest_interview.schedule_date} at {status.latest_interview.schedule_time} · {status.latest_interview.mode}</p>
            <p>{status.latest_interview.location} · Result: {status.latest_interview.result}</p>
          </section>
        ) : null}
        {status.admission ? (
          <section className="grid gap-1 text-sm">
            <h2 className="font-semibold">Admission application</h2>
            <p>Application status: {status.admission.status ?? 'Not available'}</p>
            <p>Documents submitted: {status.admission.documents_uploaded} of {status.admission.documents_required}</p>
            {status.admission.documents?.length ? (
              <ul className="mt-2 grid gap-1">
                {status.admission.documents.map((document) => (
                  <li key={document.document_type}>
                    {documentLabels[document.document_type]}: {document.verification_status}
                    {document.rejection_reason ? ` — ${document.rejection_reason}` : ''}
                  </li>
                ))}
              </ul>
            ) : null}
          </section>
        ) : null}
        {status.status === 'ADMISSION_SUCCESS' && status.admission?.student_code ? (
          <Alert>
            <AlertTitle>Congratulations! Admission confirmed</AlertTitle>
            <AlertDescription>
              {status.admission.student_name ?? 'Your child'} has been admitted to {status.admission.class_name}
              {status.admission.section ? `, Section ${status.admission.section}` : ''} for {status.admission.academic_year}.
              Student ID: <strong>{status.admission.student_code}</strong>
              {status.admission.roll_number ? ` · Roll number: ${status.admission.roll_number}` : ''}.
            </AlertDescription>
          </Alert>
        ) : null}
        {status.admission && status.status !== 'ADMISSION_SUCCESS' ? (
          <PublicAdmissionDocumentUploads
            credentials={credentials}
            documents={status.admission.documents ?? []}
            onUploaded={onRefresh}
          />
        ) : null}
        {status.status === 'ADMISSION_SUCCESS' && status.admission?.student_code ? (
          <div className="grid gap-2">
            <Button
              className="w-fit"
              disabled={letterMutation.isPending}
              onClick={() => letterMutation.mutate()}
              type="button"
            >
              {letterMutation.isPending ? 'Preparing admission letter…' : 'Download admission letter (PDF)'}
            </Button>
            {letterError ? <ErrorState title="Admission letter unavailable" description={letterError} /> : null}
          </div>
        ) : null}
        <section className="grid gap-2">
          <h2 className="font-semibold">Status history</h2>
          {status.status_timeline.length ? (
            <ol className="grid gap-2">
              {status.status_timeline.map((entry) => (
                <li className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm" key={entry.id}>
                  <strong>{entry.from_status ?? 'Submitted'} → {entry.to_status}</strong>
                  <span className="block text-xs text-slate-500">
                    {new Date(entry.created_at).toLocaleString()}
                    {entry.change_reason ? ` · ${entry.change_reason}` : ''}
                  </span>
                </li>
              ))}
            </ol>
          ) : <p className="text-sm text-slate-500">No status history was returned.</p>}
        </section>
        <div className="flex flex-wrap gap-3">
          <Link className="text-sm font-medium text-teal-800 underline-offset-4 hover:underline" to="/application/update">Update your inquiry details</Link>
          {status.status === 'INTERVIEW_PASS' && !status.admission ? (
            <Link className="text-sm font-medium text-teal-800 underline-offset-4 hover:underline" to="/application/submit">Continue to admission application</Link>
          ) : null}
        </div>
      </CardContent>
    </Card>
  )
}

export function PublicInquiryStatusPage() {
  const location = useLocation()
  const initialCode = (location.state as { inquiryCode?: string } | null)?.inquiryCode ?? ''
  const [credentials, setCredentials] = useState<Credentials | null>(null)
  const statusMutation = useMutation({
    mutationFn: (credentials: Credentials) => admissionsApi.public.getInquiryStatus(
      credentials.inquiry_code,
      credentials.email,
      credentials.parent_mobile,
    ),
  })
  const error = statusMutation.error ? toApiError(statusMutation.error) : null

  return (
    <>
      <PageHeader title="Check inquiry status" description="Verify with the inquiry code, parent email, and parent mobile number used when applying." />
      {error ? <ErrorState title="Could not verify inquiry" description={error.message} /> : null}
      <Card>
        <CardHeader><CardTitle>Verify your inquiry</CardTitle></CardHeader>
        <CardContent>
          <InquiryCredentialsForm
            buttonLabel="Check status"
            isPending={statusMutation.isPending}
            initialInquiryCode={initialCode}
            onSubmit={(submittedCredentials) => {
              setCredentials(submittedCredentials)
              statusMutation.mutate(submittedCredentials)
            }}
          />
        </CardContent>
      </Card>
      {statusMutation.data && credentials ? (
        <InquiryProgress
          credentials={credentials}
          onRefresh={() => statusMutation.mutate(credentials)}
          status={statusMutation.data}
        />
      ) : null}
    </>
  )
}

const inquiryUpdateSchema = credentialsSchema.extend({
  first_name: z.string().trim().max(100).optional(),
  middle_name: z.string().trim().max(100).optional(),
  last_name: z.string().trim().max(100).optional(),
  gender: z.enum(['', 'male', 'female', 'other']),
  father_name: z.string().trim().max(200).optional(),
  dob: z.union([z.literal(''), z.iso.date()]),
  student_mobile: z.string().trim().max(30).optional(),
  address: z.string().optional(),
  last_school: z.string().trim().max(255).optional(),
  current_class: z.string().trim().max(100).optional(),
  admission_for_class: z.string().trim().max(100).optional(),
  last_school_percentage: z.union([z.literal(''), z.coerce.number().min(0).max(100)]),
}).refine(
  (values) => [
    values.first_name, values.middle_name, values.last_name, values.gender, values.father_name,
    values.dob, values.student_mobile, values.address, values.last_school, values.current_class,
    values.admission_for_class, values.last_school_percentage,
  ].some((value) => value !== undefined && value !== ''),
  { message: 'Enter at least one inquiry detail to update.', path: ['first_name'] },
)

type InquiryUpdateInput = z.input<typeof inquiryUpdateSchema>
type InquiryUpdateValues = z.output<typeof inquiryUpdateSchema>

const inquiryUpdateFieldLabels: { key: keyof InquiryUpdateValues; label: string }[] = [
  { key: 'first_name', label: 'Student first name' },
  { key: 'middle_name', label: 'Student middle name' },
  { key: 'last_name', label: 'Student last name' },
  { key: 'gender', label: 'Gender' },
  { key: 'father_name', label: 'Parent or guardian name' },
  { key: 'dob', label: 'Date of birth' },
  { key: 'student_mobile', label: 'Student mobile' },
  { key: 'address', label: 'Residential address' },
  { key: 'last_school', label: 'Last school attended' },
  { key: 'current_class', label: 'Current class or grade' },
  { key: 'admission_for_class', label: 'Requested class or grade' },
  { key: 'last_school_percentage', label: 'Last-school percentage' },
]

const blankUpdateValues: InquiryUpdateInput = {
  inquiry_code: '',
  email: '',
  parent_mobile: '',
  first_name: '',
  middle_name: '',
  last_name: '',
  gender: '',
  father_name: '',
  dob: '',
  student_mobile: '',
  address: '',
  last_school: '',
  current_class: '',
  admission_for_class: '',
  last_school_percentage: '',
}

export function PublicInquiryUpdatePage() {
  const form = useForm<InquiryUpdateInput, unknown, InquiryUpdateValues>({
    resolver: zodResolver(inquiryUpdateSchema),
    defaultValues: blankUpdateValues,
  })
  const mutation = useMutation({
    mutationFn: (values: InquiryUpdateValues) => admissionsApi.public.updateInquiry({
      inquiry_code: values.inquiry_code,
      email: values.email,
      parent_mobile: values.parent_mobile,
      ...(values.first_name ? { first_name: values.first_name } : {}),
      ...(values.middle_name ? { middle_name: values.middle_name } : {}),
      ...(values.last_name ? { last_name: values.last_name } : {}),
      ...(values.gender !== '' ? { gender: values.gender } : {}),
      ...(values.father_name ? { father_name: values.father_name } : {}),
      ...(values.dob ? { dob: values.dob } : {}),
      ...(values.student_mobile ? { student_mobile: values.student_mobile } : {}),
      ...(values.address ? { address: values.address } : {}),
      ...(values.last_school ? { last_school: values.last_school } : {}),
      ...(values.current_class ? { current_class: values.current_class } : {}),
      ...(values.admission_for_class ? { admission_for_class: values.admission_for_class } : {}),
      ...(values.last_school_percentage !== '' ? { last_school_percentage: values.last_school_percentage } : {}),
    }),
    onSuccess: () => form.reset(blankUpdateValues),
  })
  const error = mutation.error ? toApiError(mutation.error) : null
  const updatedFields = inquiryUpdateFieldLabels.filter(({ key }) => {
    const value = mutation.variables?.[key]
    return value !== undefined && value !== ''
  })

  return (
    <>
      {mutation.data ? (
        <section aria-labelledby="inquiry-update-confirmation-title" className="rounded-2xl border border-emerald-200 bg-white p-6 shadow-lg shadow-emerald-950/5 sm:p-8">
          <span className="flex size-12 items-center justify-center rounded-full bg-emerald-100 text-emerald-700">
            <CheckCircle2 aria-hidden="true" size={26} />
          </span>
          <h1 className="mt-4 text-2xl font-semibold tracking-tight text-slate-950" id="inquiry-update-confirmation-title">
            Inquiry details updated
          </h1>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Your requested changes have been submitted successfully. The inquiry is currently <span className="font-semibold text-slate-900">{mutation.data.status}</span>.
          </p>
          <div className="mt-6 rounded-xl border border-teal-200 bg-teal-50 p-4 sm:p-5">
            <p className="text-sm font-semibold text-teal-950">Inquiry ID</p>
            <p className="mt-1 break-all font-mono text-2xl font-bold tracking-wide text-teal-900 sm:text-3xl">
              {mutation.data.inquiry_code}
            </p>
            <p className="mt-2 text-sm leading-6 text-teal-900">
              Keep this ID with your parent email and mobile number to check your status or request permitted updates.
            </p>
          </div>
          <div className="mt-5">
            <h2 className="text-sm font-semibold text-slate-900">Details submitted for update</h2>
            <ul className="mt-2 flex flex-wrap gap-2">
              {updatedFields.map(({ key, label }) => (
                <li className="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-700" key={key}>
                  {label}
                </li>
              ))}
            </ul>
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link
              className="inline-flex h-9 items-center justify-center rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/80 focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
              state={{ inquiryCode: mutation.data.inquiry_code }}
              to="/application/status"
            >
              Check your status
            </Link>
            <Link
              className="inline-flex h-9 items-center justify-center rounded-lg border border-border bg-background px-4 text-sm font-medium text-foreground transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
              to="/apply"
            >
              Apply new inquiry
            </Link>
          </div>
          <div className="mt-7 border-t border-slate-200 pt-5">
            <p className="text-sm font-semibold text-slate-900">Need assistance?</p>
            <p className="mt-1 text-sm leading-6 text-slate-600">For further information, please contact our administrative team.</p>
            <div className="mt-3 flex flex-wrap gap-x-6 gap-y-2">
              <a className="inline-flex items-center gap-2 text-sm font-semibold text-teal-800 hover:text-teal-950" href="tel:+918967558216">
                <Phone aria-hidden="true" className="size-4" />
                +91 8967558216
              </a>
              <a className="inline-flex items-center gap-2 text-sm font-semibold text-teal-800 hover:text-teal-950" href="mailto:rpsschoolroh@gmail.com">
                <Mail aria-hidden="true" className="size-4" />
                rpsschoolroh@gmail.com
              </a>
            </div>
          </div>
        </section>
      ) : (
      <>
      <PageHeader title="Update inquiry details" description="Verify your identity and submit the details you would like to update. Updates are permitted only while the inquiry is in an eligible workflow status." />
      {error ? <ErrorState title="Inquiry update failed" description={error.message} /> : null}
      <Card>
        <CardHeader>
          <CardTitle>Verify and provide changes</CardTitle>
          <CardDescription>Leave fields blank if they should remain unchanged. The parent email and phone are verification credentials and cannot be changed here.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="grid gap-4 sm:grid-cols-2" noValidate onSubmit={form.handleSubmit((values) => mutation.mutate(values))}>
            <div className="grid gap-4 sm:col-span-2 sm:grid-cols-3">
              <FormField error={form.formState.errors.inquiry_code?.message} label="Inquiry code" required>
                {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('inquiry_code')} />}
              </FormField>
              <FormField error={form.formState.errors.email?.message} label="Parent email" required>
                {({ id, describedBy }) => <Input id={id} type="email" aria-describedby={describedBy} {...form.register('email')} />}
              </FormField>
              <FormField error={form.formState.errors.parent_mobile?.message} label="Parent mobile" required>
                {({ id, describedBy }) => <Input id={id} type="tel" aria-describedby={describedBy} {...form.register('parent_mobile')} />}
              </FormField>
            </div>
            <FormField error={form.formState.errors.first_name?.message} label="Student first name">
              {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('first_name')} />}
            </FormField>
            <FormField error={form.formState.errors.middle_name?.message} label="Student middle name">
              {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('middle_name')} />}
            </FormField>
            <FormField error={form.formState.errors.last_name?.message} label="Student last name">
              {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('last_name')} />}
            </FormField>
            <FormField error={form.formState.errors.gender?.message} label="Gender">
              {({ id, describedBy }) => (
                <select id={id} aria-describedby={describedBy} className="h-10 rounded-lg border border-input bg-white px-3 text-sm" {...form.register('gender')}>
                  <option value="">No change</option><option value="male">Male</option><option value="female">Female</option><option value="other">Other</option>
                </select>
              )}
            </FormField>
            <FormField error={form.formState.errors.father_name?.message} label="Parent or guardian name">
              {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('father_name')} />}
            </FormField>
            <FormField error={form.formState.errors.dob?.message} label="Date of birth">
              {({ id, describedBy }) => <Input id={id} type="date" aria-describedby={describedBy} {...form.register('dob')} />}
            </FormField>
            <FormField error={form.formState.errors.student_mobile?.message} label="Student mobile">
              {({ id, describedBy }) => <Input id={id} type="tel" aria-describedby={describedBy} {...form.register('student_mobile')} />}
            </FormField>
            <FormField error={form.formState.errors.address?.message} label="Residential address">
              {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('address')} />}
            </FormField>
            <FormField error={form.formState.errors.last_school?.message} label="Last school attended">
              {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('last_school')} />}
            </FormField>
            <FormField error={form.formState.errors.current_class?.message} label="Current class or grade">
              {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('current_class')} />}
            </FormField>
            <FormField error={form.formState.errors.admission_for_class?.message} label="Requested class or grade">
              {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('admission_for_class')} />}
            </FormField>
            <FormField error={form.formState.errors.last_school_percentage?.message} label="Last-school percentage">
              {({ id, describedBy }) => <Input id={id} type="number" min="0" max="100" step="0.01" aria-describedby={describedBy} {...form.register('last_school_percentage')} />}
            </FormField>
            <p className="text-xs text-slate-500 sm:col-span-2">Email and parent mobile are used only to verify your authority. Contact the school office if either needs correction.</p>
            <div className="sm:col-span-2">
              <Button disabled={mutation.isPending} type="submit">{mutation.isPending ? 'Saving changes…' : 'Update inquiry'}</Button>
            </div>
          </form>
        </CardContent>
      </Card>
      </>
      )}
    </>
  )
}

const admissionDetailsSchema = z.object({
  permanent_address: z.string().max(2000).optional(),
  student_aadhaar: z.string().regex(/^\d{12}$/, 'Enter the 12-digit student Aadhaar number.'),
  parent_aadhaar: z.string().regex(/^\d{12}$/, 'Enter the 12-digit parent Aadhaar number.'),
  last_school_marks: z.string()
    .regex(/^\d+(\.\d{1,2})?$/, 'Enter valid previous-school marks.')
    .refine((value) => Number(value) <= 999999.99, 'Marks are too high.'),
  last_school_percentage: z.string()
    .regex(/^\d+(\.\d{1,2})?$/, 'Enter a valid percentage.')
    .refine((value) => Number(value) <= 100, 'Percentage must be between 0 and 100.'),
  last_school_id_or_roll_number: z.string().trim().min(1, 'Enter the previous-school ID or roll number.').max(100),
})

type AdmissionDetails = z.infer<typeof admissionDetailsSchema>

function classGradeNumber(className: string) {
  const match = className.match(/(?:grade|class)\s*(\d{1,2})|(\d{1,2})(?:st|nd|rd|th)?\s*(?:grade|class)/i)
  const grade = Number(match?.[1] ?? match?.[2])
  return Number.isInteger(grade) && grade >= 1 && grade <= 12 ? grade : null
}

export function PublicAdmissionSubmissionPage() {
  const [verifiedInquiry, setVerifiedInquiry] = useState<{
    credentials: Credentials
    status: PublicInquiryStatus
  } | null>(null)
  const [availableClasses, setAvailableClasses] = useState<
    Awaited<ReturnType<typeof admissionsApi.public.listAdmissionClasses>> | null
  >(null)
  const [classesLoading, setClassesLoading] = useState(false)
  const [classesError, setClassesError] = useState<string | null>(null)
  const [documentFiles, setDocumentFiles] = useState<Partial<Record<DocumentType, File>>>({})
  const [failedDocuments, setFailedDocuments] = useState<DocumentType[]>([])
  const [uploadedDocuments, setUploadedDocuments] = useState<DocumentType[]>([])
  const [documentErrors, setDocumentErrors] = useState<Partial<Record<DocumentType, string>>>({})
  const loadAdmissionClasses = async (requestedClass: string) => {
    setClassesLoading(true)
    setClassesError(null)
    try {
      const classes = await admissionsApi.public.listAdmissionClasses()
      setAvailableClasses(classes)
      const requestedGrade = classGradeNumber(requestedClass)
      const matchingClass = classes
        .filter((schoolClass) => requestedGrade !== null
          ? classGradeNumber(schoolClass.name) === requestedGrade
          : schoolClass.name.trim().toLocaleLowerCase() === requestedClass.trim().toLocaleLowerCase())
        .sort((left, right) => right.academic_year.localeCompare(left.academic_year))[0]
      if (!matchingClass) {
        setClassesError(`No active class is available for ${requestedClass}. Please contact the school administration.`)
      }
    } catch (error) {
      setClassesError(toApiError(error).message)
    } finally {
      setClassesLoading(false)
    }
  }
  const credentialsForm = useForm<Credentials>({
    resolver: zodResolver(credentialsSchema),
    defaultValues: {
      inquiry_code: '',
      email: '',
      parent_mobile: '',
    },
  })
  const detailsForm = useForm<AdmissionDetails>({
    resolver: zodResolver(admissionDetailsSchema),
    defaultValues: {
      permanent_address: '',
      student_aadhaar: '',
      parent_aadhaar: '',
      last_school_marks: '',
      last_school_percentage: '',
      last_school_id_or_roll_number: '',
    },
  })
  const verifyMutation = useMutation({
    mutationFn: (credentials: Credentials) => admissionsApi.public.getInquiryStatus(
      credentials.inquiry_code,
      credentials.email,
      credentials.parent_mobile,
    ),
    onSuccess: (status, credentials) => {
      setVerifiedInquiry({ credentials, status })
      if (status.status === 'INTERVIEW_PASS' && !status.admission) {
        void loadAdmissionClasses(status.admission_for_class)
      }
    },
  })
  const mutation = useMutation({
    mutationFn: async (values: AdmissionDetails) => {
      if (!verifiedInquiry || !selectedClass) {
        throw new Error('The requested class is unavailable. Please contact the school administration.')
      }
      const missing = requiredAdmissionDocuments.filter((type) => !documentFiles[type])
      if (missing.length) {
        throw new Error(`Select all required documents before submitting: ${missing.map((type) => documentLabels[type]).join(', ')}.`)
      }
      const documentsToUpload = submissionDocumentTypes.filter((type) => (
        requiredAdmissionDocuments.includes(type) || Boolean(documentFiles[type])
      ))
      const admission = await admissionsApi.public.submitAdmission({
        ...verifiedInquiry.credentials,
        class_id: selectedClass.id,
        academic_year: selectedClass.academic_year,
        permanent_address: values.permanent_address || undefined,
        student_aadhaar: values.student_aadhaar,
        parent_aadhaar: values.parent_aadhaar,
        last_school_marks: Number(values.last_school_marks),
        last_school_percentage: Number(values.last_school_percentage),
        last_school_id_or_roll_number: values.last_school_id_or_roll_number,
      })
      return {
        admission,
        ...await uploadSelectedDocuments(documentsToUpload, verifiedInquiry.credentials),
      }
    },
    onSuccess: (result) => {
      setFailedDocuments(result.failed)
      setUploadedDocuments(result.uploaded)
      setDocumentErrors(result.errors)
      detailsForm.reset({
        permanent_address: '',
        student_aadhaar: '',
        parent_aadhaar: '',
        last_school_marks: '',
        last_school_percentage: '',
        last_school_id_or_roll_number: '',
      })
      setDocumentFiles((current) => {
        const remaining = { ...current }
        result.uploaded.forEach((type) => delete remaining[type])
        return remaining
      })
    },
  })
  const retryUploadMutation = useMutation({
    mutationFn: async (types: DocumentType[]) => {
      if (!verifiedInquiry) throw new Error('Verify your inquiry before uploading documents.')
      return uploadSelectedDocuments(types, verifiedInquiry.credentials)
    },
    onSuccess: (result) => {
      setFailedDocuments(result.failed)
      setUploadedDocuments((current) => [...new Set([...current, ...result.uploaded])])
      setDocumentErrors(result.errors)
    },
  })
  async function uploadSelectedDocuments(types: DocumentType[], credentials: Credentials) {
    const uploaded: DocumentType[] = []
    const failed: DocumentType[] = []
    const errors: Partial<Record<DocumentType, string>> = {}
    for (const type of types) {
      const file = documentFiles[type]
      if (!file) {
        failed.push(type)
        errors[type] = 'Choose a file to retry this upload.'
        continue
      }
      try {
        await admissionsApi.public.uploadAdmissionDocument(credentials, type, file)
        uploaded.push(type)
      } catch (error) {
        failed.push(type)
        errors[type] = toApiError(error).message
      }
    }
    return { uploaded, failed, errors }
  }
  const verifyError = verifyMutation.error ? toApiError(verifyMutation.error) : null
  const submissionError = mutation.error ? toApiError(mutation.error) : null
  const requestedGrade = verifiedInquiry ? classGradeNumber(verifiedInquiry.status.admission_for_class) : null
  const selectedClass = (availableClasses ?? [])
    .filter((item) => requestedGrade !== null
      ? classGradeNumber(item.name) === requestedGrade
      : item.name.trim().toLocaleLowerCase() === verifiedInquiry?.status.admission_for_class.trim().toLocaleLowerCase())
    .sort((left, right) => right.academic_year.localeCompare(left.academic_year))[0]
  const canSubmitAdmission = verifiedInquiry?.status.status === 'INTERVIEW_PASS'
    && !verifiedInquiry.status.admission
  const resetVerification = () => {
    setVerifiedInquiry(null)
    verifyMutation.reset()
    setAvailableClasses(null)
    setClassesError(null)
    mutation.reset()
    retryUploadMutation.reset()
    detailsForm.reset({
      permanent_address: '',
      student_aadhaar: '',
      parent_aadhaar: '',
      last_school_marks: '',
      last_school_percentage: '',
      last_school_id_or_roll_number: '',
    })
    setDocumentFiles({})
    setFailedDocuments([])
    setUploadedDocuments([])
    setDocumentErrors({})
  }

  return (
    <>
      <PageHeader
        title="Submit admission application"
        description="First verify your inquiry. After verification, the application details and document uploads appear when the inquiry is eligible (interview passed)."
      />
      <Card>
        <CardHeader>
          <CardTitle>{verifiedInquiry ? 'Admission application details' : 'Verify your inquiry'}</CardTitle>
          <CardDescription>
            Step 1: enter the inquiry code, parent email, and mobile number from your inquiry confirmation.
            After verification, you can provide Aadhaar numbers, previous-school results and ID, and upload
            the required documents. Parents submit the documents; school staff review them.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!verifiedInquiry ? (
            <form
              className="grid gap-4 sm:grid-cols-2"
              noValidate
              onSubmit={credentialsForm.handleSubmit((credentials) => verifyMutation.mutate(credentials))}
            >
              <FormField error={credentialsForm.formState.errors.inquiry_code?.message} label="Inquiry code" required>
                {({ id, describedBy }) => <Input id={id} autoComplete="off" aria-describedby={describedBy} {...credentialsForm.register('inquiry_code')} />}
              </FormField>
              <FormField error={credentialsForm.formState.errors.email?.message} label="Parent email" required>
                {({ id, describedBy }) => <Input id={id} type="email" autoComplete="email" aria-describedby={describedBy} {...credentialsForm.register('email')} />}
              </FormField>
              <FormField error={credentialsForm.formState.errors.parent_mobile?.message} label="Parent mobile" required>
                {({ id, describedBy }) => <Input id={id} type="tel" autoComplete="tel" aria-describedby={describedBy} {...credentialsForm.register('parent_mobile')} />}
              </FormField>
              <div className="sm:col-span-2">
                <Button disabled={verifyMutation.isPending} type="submit">
                  {verifyMutation.isPending ? 'Verifying inquiry…' : 'Verify inquiry'}
                </Button>
              </div>
            </form>
          ) : (
            <div className="grid gap-5">
              <Alert>
                <AlertTitle>Inquiry {verifiedInquiry.status.inquiry_code}</AlertTitle>
                <AlertDescription>
                  Current status: {verifiedInquiry.status.status}. Requested class: {verifiedInquiry.status.admission_for_class}.
                </AlertDescription>
              </Alert>
              {verifiedInquiry.status.admission ? (
                <Alert>
                  <AlertTitle>Your admission application is under review</AlertTitle>
                  <AlertDescription>
                    Your application has already been submitted. The school administration will update you shortly. For more information, contact administration at{' '}
                    <a className="font-semibold underline" href="tel:+918967558216">+91 8967558216</a>
                    {' '}or{' '}
                    <a className="font-semibold underline" href="mailto:rpsschoolroh@gmail.com">rpsschoolroh@gmail.com</a>.
                  </AlertDescription>
                </Alert>
              ) : null}
              {!verifiedInquiry.status.admission && !canSubmitAdmission ? (
                <Alert>
                  <AlertTitle>Admission application is not ready yet</AlertTitle>
                  <AlertDescription>
                    The school must record an interview pass before an admission application can be submitted.
                    {' '}Please check your inquiry status again after the school updates it.
                  </AlertDescription>
                </Alert>
              ) : !verifiedInquiry.status.admission && mutation.data ? (
                <div className="grid gap-3">
                  <SuccessState
                    title="Admission application submitted"
                    description={`Your admission application is under review. The school administration will update you shortly. ${uploadedDocuments.filter((type) => requiredAdmissionDocuments.includes(type)).length} of ${requiredAdmissionDocuments.length} required documents uploaded.`}
                  />
                  <p className="text-sm text-slate-600">
                    For more information, contact administration at{' '}
                    <a className="font-semibold text-teal-800 underline" href="tel:+918967558216">+91 8967558216</a>
                    {' '}or{' '}
                    <a className="font-semibold text-teal-800 underline" href="mailto:rpsschoolroh@gmail.com">rpsschoolroh@gmail.com</a>.
                  </p>
                  {failedDocuments.length ? (
                    <section className="grid gap-3 rounded-lg border border-amber-300 bg-amber-50 p-4">
                      <div>
                        <h2 className="font-semibold">Some documents need another upload attempt</h2>
                        <p className="text-sm text-slate-700">Your application is saved. Select replacements for missing files and retry; you do not need to submit the application again.</p>
                      </div>
                      <div className="grid gap-3 sm:grid-cols-2">
                        {failedDocuments.map((type) => (
                          <FormField
                            error={documentErrors[type]}
                            key={type}
                            label={documentLabels[type]}
                            required
                          >
                            {({ id }) => (
                              <input
                                accept=".pdf,.jpg,.jpeg,.png"
                                className="block w-full text-sm"
                                id={id}
                                onChange={(event) => {
                                  const file = event.currentTarget.files?.[0]
                                  if (file) setDocumentFiles((current) => ({ ...current, [type]: file }))
                                }}
                                type="file"
                              />
                            )}
                          </FormField>
                        ))}
                      </div>
                      <Button
                        className="w-fit"
                        disabled={retryUploadMutation.isPending || failedDocuments.some((type) => !documentFiles[type])}
                        onClick={() => retryUploadMutation.mutate(failedDocuments)}
                        type="button"
                      >
                        {retryUploadMutation.isPending ? 'Retrying uploads…' : 'Retry failed document uploads'}
                      </Button>
                    </section>
                  ) : null}
                  <Link
                    className="w-fit text-sm font-medium text-teal-800 underline-offset-4 hover:underline"
                    state={{ inquiryCode: verifiedInquiry.credentials.inquiry_code }}
                    to="/application/status"
                  >
                    Check application status
                  </Link>
                </div>
              ) : !verifiedInquiry.status.admission ? (
                <>
                  {classesLoading ? <div role="status">Loading available classes…</div> : null}
                  {classesError ? (
                    <ErrorState
                      description={classesError}
                      onRetry={() => void loadAdmissionClasses(verifiedInquiry.status.admission_for_class)}
                      title="Available classes could not be loaded"
                    />
                  ) : null}
                  {availableClasses && !availableClasses.length ? (
                    <Alert>
                      <AlertTitle>Applications are not open for any classes yet</AlertTitle>
                      <AlertDescription>Please contact the school office for application availability.</AlertDescription>
                    </Alert>
                  ) : null}
                  {availableClasses?.length ? (
                    <>
                      <section aria-label="Admission class assignment" className="grid gap-2 rounded-lg border border-slate-200 p-4 sm:grid-cols-3">
                        <div>
                          <h2 className="text-sm font-medium">Student name</h2>
                          <p>{verifiedInquiry.status.student_name}</p>
                        </div>
                        <div>
                          <h2 className="text-sm font-medium">Class</h2>
                          <p>{verifiedInquiry.status.admission_for_class}</p>
                        </div>
                        <div>
                          <h2 className="text-sm font-medium">Academic year</h2>
                          <p>Assigned by administration during enrollment</p>
                        </div>
                        <p className="text-sm text-slate-600 sm:col-span-3">
                          Class and academic year are based on your inquiry. Administration will assign the section and academic year during enrollment.
                        </p>
                      </section>
                      {availableClasses.length > 0 && !selectedClass ? (
                        <Alert>
                          <AlertTitle>Requested class is unavailable</AlertTitle>
                          <AlertDescription>Please contact the school administration before submitting this application.</AlertDescription>
                        </Alert>
                      ) : null}
                      <form
                        className="grid gap-4"
                        noValidate
                        onSubmit={detailsForm.handleSubmit((values) => mutation.mutate(values))}
                      >
                        <FormField label="Permanent address">
                          {({ id, describedBy }) => (
                            <textarea
                              className="min-h-24 w-full rounded-lg border border-input bg-white p-3 text-sm"
                              id={id}
                              aria-describedby={describedBy}
                              {...detailsForm.register('permanent_address')}
                            />
                          )}
                        </FormField>
                        <div className="grid gap-4 sm:grid-cols-2">
                          <FormField
                            description="Enter all 12 digits. The number is encrypted in storage; staff see only a masked value."
                            error={detailsForm.formState.errors.student_aadhaar?.message}
                            label="Student Aadhaar number"
                            required
                          >
                            {({ id, describedBy }) => <Input id={id} autoComplete="off" inputMode="numeric" maxLength={12} aria-describedby={describedBy} {...detailsForm.register('student_aadhaar')} />}
                          </FormField>
                          <FormField
                            description="Enter all 12 digits. The number is encrypted in storage; staff see only a masked value."
                            error={detailsForm.formState.errors.parent_aadhaar?.message}
                            label="Parent / guardian Aadhaar number"
                            required
                          >
                            {({ id, describedBy }) => <Input id={id} autoComplete="off" inputMode="numeric" maxLength={12} aria-describedby={describedBy} {...detailsForm.register('parent_aadhaar')} />}
                          </FormField>
                          <FormField error={detailsForm.formState.errors.last_school_marks?.message} label="Marks obtained at last school" required>
                            {({ id, describedBy }) => <Input id={id} inputMode="decimal" aria-describedby={describedBy} {...detailsForm.register('last_school_marks')} />}
                          </FormField>
                          <FormField error={detailsForm.formState.errors.last_school_percentage?.message} label="Last-school percentage" required>
                            {({ id, describedBy }) => <Input id={id} inputMode="decimal" aria-describedby={describedBy} {...detailsForm.register('last_school_percentage')} />}
                          </FormField>
                          <FormField error={detailsForm.formState.errors.last_school_id_or_roll_number?.message} label="Last-school student ID / roll number" required>
                            {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...detailsForm.register('last_school_id_or_roll_number')} />}
                          </FormField>
                        </div>
                        <section className="grid gap-3">
                          <div>
                            <h2 className="font-semibold">Admission documents</h2>
                            <p className="text-sm text-slate-600">Upload the four required documents. Migration and character certificates are optional and may be provided later. Files can be PDF, JPG, JPEG, or PNG.</p>
                          </div>
                          <div className="grid gap-3 sm:grid-cols-2">
                            {submissionDocumentTypes.map((type) => {
                              const required = requiredAdmissionDocuments.includes(type)
                              return (
                              <FormField
                                description={required ? undefined : 'Optional — you may provide this later.'}
                                key={type}
                                label={documentLabels[type]}
                                required={required}
                              >
                                {({ id }) => (
                                  <input
                                    accept=".pdf,.jpg,.jpeg,.png"
                                    className="block w-full text-sm file:mr-3 file:rounded-md file:border-0 file:bg-slate-100 file:px-3 file:py-2"
                                    id={id}
                                    onChange={(event) => {
                                      const file = event.currentTarget.files?.[0]
                                      if (file) setDocumentFiles((current) => ({ ...current, [type]: file }))
                                    }}
                                    required={required}
                                    type="file"
                                  />
                                )}
                              </FormField>
                              )
                            })}
                          </div>
                        </section>
                        {submissionError ? (
                          <ErrorState title="Admission submission failed" description={submissionError.message} />
                        ) : null}
                        <div>
                          <Button disabled={mutation.isPending || !selectedClass} type="submit">
                            {mutation.isPending ? 'Submitting application and documents…' : 'Submit admission application'}
                          </Button>
                        </div>
                      </form>
                    </>
                  ) : null}
                </>
              ) : null}
              {!mutation.data && !verifiedInquiry.status.admission ? (
                <Button className="w-fit" onClick={resetVerification} type="button" variant="outline">
                  Change inquiry details
                </Button>
              ) : null}
            </div>
          )}
          {verifyError && !verifiedInquiry ? (
            <ErrorState title="Inquiry verification failed" description={verifyError.message} />
          ) : null}
        </CardContent>
      </Card>
    </>
  )
}

export { PublicPortalLayout }
