import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { z } from 'zod'
import { PermissionGate } from '@/components/auth/permission-gate'
import { FormDialog } from '@/components/school/form-dialog'
import { RecordList } from '@/components/school/record-list'
import { FormField } from '@/components/ui/form-field'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { ErrorState, LoadingState, SuccessState } from '@/components/ui/async-state'
import { Input } from '@/components/ui/input'
import { PageHeader } from '@/components/ui/page-header'
import { SearchField } from '@/components/ui/search-field'
import { SearchableSelect } from '@/components/ui/searchable-select'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { admissionsApi, type Inquiry, type InquiryStatus } from '@/features/admissions/admissions-api'
import { schoolApi } from '@/features/school/school-api'
import { toApiError } from '@/lib/api/api-error'
import { useAuth } from '@/features/auth/auth-context'

function localDateString(date: Date) {
  return [
    date.getFullYear(),
    String(date.getMonth() + 1).padStart(2, '0'),
    String(date.getDate()).padStart(2, '0'),
  ].join('-')
}

const pageSize = 10
const inquiryStatuses: InquiryStatus[] = [
  'PENDING',
  'UNDER_REVIEW',
  'PROCESSING',
  'INTERVIEW_SCHEDULED',
  'INTERVIEW_PASS',
  'INTERVIEW_FAIL',
  'DOCUMENT_PENDING',
  'DOCUMENT_VERIFICATION',
  'ADMISSION_SUCCESS',
  'REJECTED',
]

const inquirySchema = z.object({
  first_name: z.string().trim().min(1).max(100),
  middle_name: z.string().trim().max(100).optional(),
  last_name: z.string().trim().min(1).max(100),
  gender: z.enum(['male', 'female', 'other']),
  father_name: z.string().trim().min(1).max(200),
  dob: z.iso.date().refine(
    (value) => value <= localDateString(new Date()),
    'Date of birth cannot be in the future.',
  ),
  student_mobile: z.string().trim().max(30).optional(),
  parent_mobile: z.string().trim().min(5).max(30),
  email: z.string().email(),
  address: z.string().trim().min(5),
  last_school: z.string().trim().min(1).max(255),
  current_class: z.string().trim().min(1).max(100),
  admission_for_class: z.string().trim().min(1).max(100),
})

type InquiryFormValues = z.infer<typeof inquirySchema>

const initialInquiryValues: InquiryFormValues = {
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

function InquiryCreateDialog({
  open,
  onOpenChange,
  onCreated,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  onCreated: (code: string) => void
}) {
  const [classId, setClassId] = useState('')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const queryClient = useQueryClient()
  const classesQuery = useQuery({
    queryKey: ['classes', 'inquiry-options'],
    queryFn: () => schoolApi.classes.list(
      { page: 1, limit: 100, sort_by: 'name', sort_order: 'asc' },
      { status: 'active' },
    ),
    enabled: open,
  })
  const form = useForm<InquiryFormValues>({
    resolver: zodResolver(inquirySchema),
    defaultValues: initialInquiryValues,
  })
  const mutation = useMutation({
    mutationFn: (values: InquiryFormValues) => admissionsApi.inquiries.create({
      ...values,
      middle_name: values.middle_name || null,
      student_mobile: values.student_mobile || null,
      admission_for_class_id: classId ? Number(classId) : undefined,
    }),
    onSuccess: async (created) => {
      await queryClient.invalidateQueries({ queryKey: ['inquiries'] })
      form.reset(initialInquiryValues)
      setClassId('')
      setErrorMessage(null)
      onOpenChange(false)
      onCreated(created.inquiry_code)
    },
    onError: (error) => {
      const apiError = toApiError(error)
      setErrorMessage(apiError.status === 409
        ? `A possible duplicate inquiry was rejected: ${apiError.message} Check the existing inquiry list before submitting again. The API does not identify the matching record.`
        : apiError.message)
    },
  })

  return (
    <FormDialog
      description="Submit an inquiry using the backend's public intake endpoint. The API checks for a duplicate using the student's first and last name, parent name, and date of birth."
      onOpenChange={onOpenChange}
      open={open}
      title="Create inquiry"
    >
      {errorMessage ? (
        <Alert className="mb-3" variant="destructive">
          <AlertTitle>Inquiry was not created</AlertTitle>
          <AlertDescription>{errorMessage}</AlertDescription>
        </Alert>
      ) : null}
      <form className="grid gap-4 sm:grid-cols-2" noValidate onSubmit={form.handleSubmit((values) => {
        setErrorMessage(null)
        mutation.mutate(values)
      })}>
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
          {({ id, describedBy }) => <Input id={id} max={localDateString(new Date())} type="date" aria-describedby={describedBy} {...form.register('dob')} />}
        </FormField>
        <FormField error={form.formState.errors.parent_mobile?.message} label="Parent mobile" required>
          {({ id, describedBy }) => <Input id={id} type="tel" aria-describedby={describedBy} {...form.register('parent_mobile')} />}
        </FormField>
        <FormField error={form.formState.errors.student_mobile?.message} label="Student mobile">
          {({ id, describedBy }) => <Input id={id} type="tel" aria-describedby={describedBy} {...form.register('student_mobile')} />}
        </FormField>
        <FormField error={form.formState.errors.email?.message} label="Parent email" required>
          {({ id, describedBy }) => <Input id={id} type="email" aria-describedby={describedBy} {...form.register('email')} />}
        </FormField>
        <FormField error={form.formState.errors.address?.message} label="Residential address" required>
          {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('address')} />}
        </FormField>
        <FormField error={form.formState.errors.last_school?.message} label="Last school" required>
          {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('last_school')} />}
        </FormField>
        <FormField error={form.formState.errors.current_class?.message} label="Current class or grade" required>
          {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('current_class')} />}
        </FormField>
        <FormField error={form.formState.errors.admission_for_class?.message} label="Requested class or grade" required>
          {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('admission_for_class')} />}
        </FormField>
        {classesQuery.error ? (
          <p className="text-sm text-destructive sm:col-span-2">Class mapping options unavailable: {toApiError(classesQuery.error).message}</p>
        ) : classesQuery.data?.items.length ? (
          <div className="sm:col-span-2">
            <SearchableSelect
              label="Optional catalog class mapping"
              onChange={setClassId}
              options={classesQuery.data.items.map((item) => ({
                value: String(item.id),
                label: `${item.name}${item.section ? ` · ${item.section}` : ''} · ${item.academic_year}`,
              }))}
              value={classId}
            />
          </div>
        ) : null}
        <div className="flex justify-end gap-2 sm:col-span-2">
          <Button onClick={() => onOpenChange(false)} type="button" variant="outline">Cancel</Button>
          <Button disabled={mutation.isPending} type="submit">{mutation.isPending ? 'Submitting…' : 'Submit inquiry'}</Button>
        </div>
      </form>
    </FormDialog>
  )
}

function InquiryDetailDialog({
  inquiryId,
  open,
  onOpenChange,
  onAdmissionCreated,
}: {
  inquiryId: number | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onAdmissionCreated: (code: string) => void
}) {
  const enabled = open && inquiryId !== null
  const inquiryQuery = useQuery({
    queryKey: ['inquiries', inquiryId],
    queryFn: () => admissionsApi.inquiries.get(inquiryId!),
    enabled,
  })
  const inquiry = inquiryQuery.data

  return (
    <>
      <Dialog onOpenChange={onOpenChange} open={open}>
        <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-3xl">
          <DialogHeader>
            <DialogTitle>Inquiry details{inquiry ? ` — ${inquiry.inquiry_code}` : ''}</DialogTitle>
            <DialogDescription>Review the submitted inquiry, status history, and staff-only fields.</DialogDescription>
          </DialogHeader>
          {inquiryQuery.isLoading ? <LoadingState label="Loading inquiry details" /> : null}
          {inquiryQuery.error ? <ErrorState description={toApiError(inquiryQuery.error).message} onRetry={() => void inquiryQuery.refetch()} /> : null}
          {inquiry ? (
            <div className="grid gap-4">
              <section className="grid gap-2 rounded-lg border border-slate-200 p-4 sm:grid-cols-2">
                <p><strong>Student:</strong> {inquiry.first_name} {inquiry.middle_name} {inquiry.last_name}</p>
                <p><strong>Status:</strong> {inquiry.status}</p>
                <p><strong>Parent:</strong> {inquiry.father_name}</p>
                <p><strong>Date of birth:</strong> {inquiry.date_of_birth}</p>
                <p><strong>Email:</strong> {inquiry.email}</p>
                <p><strong>Parent mobile:</strong> {inquiry.parent_mobile}</p>
                <p><strong>Requested class:</strong> {inquiry.admission_for_class}</p>
                <p><strong>Last school:</strong> {inquiry.last_school}</p>
                <p className="sm:col-span-2"><strong>Address:</strong> {inquiry.address}</p>
                {inquiry.rejection_reason ? <p className="text-destructive sm:col-span-2"><strong>Rejection reason:</strong> {inquiry.rejection_reason}</p> : null}
              </section>
              <section className="grid gap-2">
                <h3 className="text-sm font-semibold">Status history</h3>
                {inquiry.status_timeline.length ? (
                  <ol className="grid gap-2">
                    {inquiry.status_timeline.map((item) => (
                      <li className="rounded-md border border-slate-200 px-3 py-2 text-sm" key={item.id}>
                        <strong>{item.from_status ?? 'Submitted'} → {item.to_status}</strong>
                        <span className="block text-xs text-slate-500">{new Date(item.created_at).toLocaleString()} {item.change_reason ? `· ${item.change_reason}` : ''}</span>
                      </li>
                    ))}
                  </ol>
                ) : <p className="text-sm text-slate-500">No status history was returned.</p>}
              </section>
              <InquiryStaffActions
                key={inquiry.id}
                inquiry={inquiry}
                onAdmissionCreated={onAdmissionCreated}
                onClose={() => onOpenChange(false)}
              />
            </div>
          ) : null}
        </DialogContent>
      </Dialog>
    </>
  )
}

function InquiryStaffActions({
  inquiry,
  onAdmissionCreated,
  onClose,
}: {
  inquiry: Inquiry
  onAdmissionCreated: (code: string) => void
  onClose: () => void
}) {
  const { user } = useAuth()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [notes, setNotes] = useState(inquiry.internal_notes ?? '')
  const [classId, setClassId] = useState(inquiry.admission_for_class_id ? String(inquiry.admission_for_class_id) : '')
  const [rejectionReason, setRejectionReason] = useState('')
  const [applicationOpen, setApplicationOpen] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const canEdit = user?.permissions?.includes('inquiries.review') ?? false
  const canProcess = user?.permissions?.includes('inquiries.update') ?? false
  const canReject = user?.permissions?.includes('inquiries.reject') ?? false
  const canReadClasses = user?.permissions?.includes('classes.read') ?? false
  const classesQuery = useQuery({
    queryKey: ['classes', 'inquiry-edit-options'],
    queryFn: () => schoolApi.classes.list(
      { page: 1, limit: 100, sort_by: 'name', sort_order: 'asc' },
      { status: 'active' },
    ),
    enabled: canReadClasses,
  })
  const reviewMutation = useMutation({
    mutationFn: (action: 'start' | 'process' | 'reject') => {
      if (action === 'start') return admissionsApi.inquiries.startReview(inquiry.id, notes || undefined)
      if (action === 'process') return admissionsApi.inquiries.markProcessing(inquiry.id, notes || undefined)
      return admissionsApi.inquiries.reject(inquiry.id, rejectionReason)
    },
    onSuccess: async (updated) => {
      setSuccessMessage(`Inquiry status is now ${updated.status}.`)
      setErrorMessage(null)
      setRejectionReason('')
      await queryClient.invalidateQueries({ queryKey: ['inquiries'] })
      await queryClient.invalidateQueries({ queryKey: ['inquiries', inquiry.id] })
    },
    onError: (error) => setErrorMessage(toApiError(error).message),
  })
  const editMutation = useMutation({
    mutationFn: () => admissionsApi.inquiries.updateStaff(inquiry.id, {
      ...(classId ? { admission_for_class_id: Number(classId) } : {}),
      internal_notes: notes,
    }),
    onSuccess: async () => {
      setSuccessMessage('Staff notes and class mapping saved.')
      setErrorMessage(null)
      await queryClient.invalidateQueries({ queryKey: ['inquiries'] })
      await queryClient.invalidateQueries({ queryKey: ['inquiries', inquiry.id] })
    },
    onError: (error) => setErrorMessage(toApiError(error).message),
  })
  const isLocked = inquiry.status === 'ADMISSION_SUCCESS'
    || inquiry.status === 'INTERVIEW_FAIL'
    || inquiry.status === 'REJECTED'

  return (
    <div className="grid gap-3">
      {successMessage ? <SuccessState title="Inquiry updated" description={successMessage} /> : null}
      {errorMessage ? <ErrorState title="Inquiry action failed" description={errorMessage} /> : null}
      <section className="grid gap-2">
        <h3 className="text-sm font-semibold">Staff-editable fields</h3>
        <p className="text-xs text-slate-500">The staff API permits internal notes and catalog class mapping only. Applicant profile edits are not available in the staff API.</p>
        <label className="grid gap-2 text-sm font-medium">
          Internal notes
          <textarea className="min-h-20 rounded-lg border border-input bg-white p-3 text-sm" onChange={(event) => setNotes(event.target.value)} value={notes} />
        </label>
        {canReadClasses ? (
          classesQuery.error ? <ErrorState description={toApiError(classesQuery.error).message} onRetry={() => void classesQuery.refetch()} /> : (
            <SearchableSelect
              label="Requested catalog class"
              onChange={setClassId}
              options={(classesQuery.data?.items ?? []).map((item) => ({
                value: String(item.id),
                label: `${item.name}${item.section ? ` · ${item.section}` : ''} · ${item.academic_year}`,
              }))}
              value={classId}
            />
          )
        ) : <p className="text-sm text-slate-500">Class mapping requires the classes.read permission.</p>}
        {canEdit ? <Button disabled={editMutation.isPending} onClick={() => editMutation.mutate()} type="button" variant="outline">Save staff fields</Button> : null}
      </section>
      <div className="flex flex-wrap gap-2">
        {canEdit && inquiry.status === 'PENDING' ? <Button disabled={reviewMutation.isPending} onClick={() => reviewMutation.mutate('start')}>Start review</Button> : null}
        {canProcess && inquiry.status === 'UNDER_REVIEW' ? <Button disabled={reviewMutation.isPending} onClick={() => reviewMutation.mutate('process')}>Mark processing</Button> : null}
        {canReject && !isLocked ? (
          <div className="flex min-w-full flex-wrap gap-2 sm:min-w-0">
            <Input aria-label="Inquiry rejection reason" onChange={(event) => setRejectionReason(event.target.value)} placeholder="Required rejection reason" value={rejectionReason} />
            <Button disabled={rejectionReason.trim().length < 3 || reviewMutation.isPending} onClick={() => reviewMutation.mutate('reject')} type="button" variant="destructive">Reject inquiry</Button>
          </div>
        ) : null}
        {inquiry.status === 'PROCESSING' || inquiry.status === 'INTERVIEW_SCHEDULED' ? (
          <Button onClick={() => {
            onClose()
            navigate('/interviews', { state: { inquiryId: inquiry.id } })
          }} type="button" variant="outline">Open interviews</Button>
        ) : null}
        {inquiry.status === 'INTERVIEW_PASS' && user?.permissions?.includes('admissions.create') && canReadClasses ? (
          <Button onClick={() => setApplicationOpen(true)} type="button">Create admission application</Button>
        ) : null}
      </div>
      <AdmissionCreateDialog
        key={inquiry.id}
        inquiry={inquiry}
        onCreated={onAdmissionCreated}
        onOpenChange={setApplicationOpen}
        open={applicationOpen}
      />
    </div>
  )
}

function AdmissionCreateDialog({
  inquiry,
  open,
  onOpenChange,
  onCreated,
}: {
  inquiry: Inquiry | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onCreated: (code: string) => void
}) {
  const [classId, setClassId] = useState('')
  const [academicYear, setAcademicYear] = useState('')
  const [section, setSection] = useState('')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const queryClient = useQueryClient()
  const classesQuery = useQuery({
    queryKey: ['classes', 'admission-options'],
    queryFn: () => schoolApi.classes.list(
      { page: 1, limit: 100, sort_by: 'name', sort_order: 'asc' },
      { status: 'active' },
    ),
    enabled: open,
  })
  const selectedClass = classesQuery.data?.items.find((item) => item.id === Number(classId))
  const mutation = useMutation({
    mutationFn: () => {
      if (!inquiry || !classId || !academicYear) throw new Error('Select an active class and academic year.')
      return admissionsApi.admissions.createFromInquiry(inquiry.id, {
        class_id: Number(classId),
        academic_year: academicYear,
        section: section || null,
        permanent_address: inquiry.address,
      })
    },
    onSuccess: async (admission) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['admissions'] }),
        queryClient.invalidateQueries({ queryKey: ['inquiries'] }),
      ])
      onOpenChange(false)
      onCreated(admission.admission_code)
    },
    onError: (error) => setErrorMessage(toApiError(error).message),
  })
  return (
    <FormDialog
      description="The backend accepts admission creation only after the inquiry has passed an interview."
      onOpenChange={onOpenChange}
      open={open}
      title="Create admission application"
    >
      {errorMessage ? <ErrorState title="Admission was not created" description={errorMessage} /> : null}
      {classesQuery.error ? <ErrorState description={toApiError(classesQuery.error).message} onRetry={() => void classesQuery.refetch()} /> : (
        <SearchableSelect
          label="Active class"
          onChange={(value) => {
            setClassId(value)
            const item = classesQuery.data?.items.find((option) => option.id === Number(value))
            setAcademicYear(item?.academic_year ?? '')
            setSection(item?.section ?? '')
          }}
          options={(classesQuery.data?.items ?? []).map((item) => ({
            value: String(item.id),
            label: `${item.name}${item.section ? ` · ${item.section}` : ''} · ${item.academic_year}`,
          }))}
          value={classId}
        />
      )}
      {selectedClass ? (
        <p className="text-sm text-slate-600">Academic year: {academicYear} · Section: {section || 'Not specified'}</p>
      ) : null}
      <div className="flex justify-end gap-2">
        <Button onClick={() => onOpenChange(false)} type="button" variant="outline">Cancel</Button>
        <Button disabled={!classId || !academicYear || mutation.isPending} onClick={() => mutation.mutate()}>
          {mutation.isPending ? 'Creating…' : 'Create application'}
        </Button>
      </div>
    </FormDialog>
  )
}

export function InquiriesPage() {
  const { user } = useAuth()
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<InquiryStatus | ''>('')
  const [classId, setClassId] = useState('')
  const [page, setPage] = useState(1)
  const [selectedInquiryId, setSelectedInquiryId] = useState<number | null>(null)
  const [createOpen, setCreateOpen] = useState(false)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const canReadClasses = user?.permissions?.includes('classes.read') ?? false
  const query = useQuery({
    queryKey: ['inquiries', { search, status, classId, page }],
    queryFn: () => admissionsApi.inquiries.list(
      { page, limit: pageSize, sort_by: 'created_at', sort_order: 'desc' },
      {
        search: search || undefined,
        status: status || undefined,
        admission_for_class_id: classId ? Number(classId) : undefined,
      },
    ),
  })
  const classesQuery = useQuery({
    queryKey: ['classes', 'inquiry-filter-options'],
    queryFn: () => schoolApi.classes.list(
      { page: 1, limit: 100, sort_by: 'name', sort_order: 'asc' },
      {},
    ),
    enabled: canReadClasses,
  })
  const columns = [
    { id: 'code', header: 'Inquiry code', cell: (inquiry: Inquiry) => <span className="font-semibold">{inquiry.inquiry_code}</span> },
    { id: 'student', header: 'Student', cell: (inquiry: Inquiry) => `${inquiry.first_name} ${inquiry.last_name}` },
    { id: 'requested-class', header: 'Requested class', cell: (inquiry: Inquiry) => inquiry.admission_for_class },
    { id: 'status', header: 'Status', cell: (inquiry: Inquiry) => inquiry.status },
    { id: 'created', header: 'Submitted', cell: (inquiry: Inquiry) => new Date(inquiry.created_at).toLocaleDateString() },
    { id: 'actions', header: 'Actions', cell: (inquiry: Inquiry) => (
      <Button onClick={() => setSelectedInquiryId(inquiry.id)} size="sm" variant="outline">Details</Button>
    ) },
  ]

  return (
    <>
      <PageHeader
        actions={<PermissionGate anyOf={['inquiries.create']}><Button onClick={() => setCreateOpen(true)}>Create inquiry</Button></PermissionGate>}
        description="Review public intake submissions, search and filter the pipeline, and perform only API-supported status transitions."
        title="Inquiries"
      />
      {successMessage ? <SuccessState title="Inquiry submitted" description={successMessage} /> : null}
      <div className="mt-5">
        <RecordList
          columns={columns}
          emptyMessage="No inquiries match these filters."
          error={query.error ? toApiError(query.error).message : undefined}
          getRowId={(inquiry) => inquiry.id}
          isLoading={query.isLoading}
          onPageChange={setPage}
          onRetry={() => void query.refetch()}
          pagination={query.data?.pagination}
          rows={query.data?.items ?? []}
          toolbar={
            <div className="grid min-w-0 gap-3 sm:grid-cols-2 xl:grid-cols-3">
              <SearchField
                label="Search inquiries"
                onChange={(value) => {
                  setSearch(value)
                  setPage(1)
                }}
                placeholder="Search name, code, email, or mobile"
                showLabel
                value={search}
              />
              <label className="grid min-w-0 gap-2 text-sm font-medium" htmlFor="inquiry-status-filter">
                Filter by status
                <select
                  className="h-10 w-full min-w-0 rounded-lg border border-input bg-white px-3 text-sm"
                  id="inquiry-status-filter"
                  onChange={(event) => {
                    setStatus(event.target.value as InquiryStatus | '')
                    setPage(1)
                  }}
                  value={status}
                >
                  <option value="">All statuses</option>
                  {inquiryStatuses.map((item) => <option key={item} value={item}>{item}</option>)}
                </select>
              </label>
              {canReadClasses ? classesQuery.error ? (
                <p className="text-sm text-destructive">Class filter unavailable: {toApiError(classesQuery.error).message}</p>
              ) : (
                <SearchableSelect
                  label="Filter by requested catalog class"
                  onChange={(value) => {
                    setClassId(value)
                    setPage(1)
                  }}
                  options={(classesQuery.data?.items ?? []).map((item) => ({
                    value: String(item.id),
                    label: `${item.name}${item.section ? ` · ${item.section}` : ''} · ${item.academic_year}`,
                  }))}
                  value={classId}
                />
              ) : null}
            </div>
          }
        />
      </div>
      <InquiryCreateDialog
        onCreated={(code) => setSuccessMessage(`Inquiry ${code} was created. Save this code for parent status tracking.`)}
        onOpenChange={setCreateOpen}
        open={createOpen}
      />
      <InquiryDetailDialog
        inquiryId={selectedInquiryId}
        onAdmissionCreated={(code) => setSuccessMessage(`Admission application ${code} was created.`)}
        onOpenChange={(open) => {
          if (!open) setSelectedInquiryId(null)
        }}
        open={selectedInquiryId !== null}
      />
    </>
  )
}
