import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { ClassRecordSelector } from '@/components/school/class-record-selector'
import { AdmissionDocumentsPanel } from '@/features/admissions/admission-documents-panel'
import {
  admissionsApi,
  REQUIRED_ADMISSION_DOCUMENT_TYPES,
  type Admission,
} from '@/features/admissions/admissions-api'
import { FormDialog } from '@/components/school/form-dialog'
import { RecordList } from '@/components/school/record-list'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { EmptyState, ErrorState, LoadingState, SuccessState } from '@/components/ui/async-state'
import { FormField } from '@/components/ui/form-field'
import { Input } from '@/components/ui/input'
import { PageHeader } from '@/components/ui/page-header'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { schoolApi } from '@/features/school/school-api'
import { toApiError } from '@/lib/api/api-error'
import { useAuth } from '@/features/auth/auth-context'

const pageSize = 10
const admissionStatuses: Admission['status'][] = [
  'draft',
  'submitted',
  'document_pending',
  'document_verification',
  'approved',
  'rejected',
]

const admissionEditSchema = z.object({
  academic_year: z.string().trim().min(4).max(20),
  section: z.string().trim().max(20).optional(),
  permanent_address: z.string().optional(),
  temporary_address: z.string().optional(),
  nationality: z.string().max(100).optional(),
  disability: z.string().max(255).optional(),
  blood_group: z.string().max(10).optional(),
  reason_for_school_change: z.string().optional(),
  notes: z.string().optional(),
})
type AdmissionEditValues = z.infer<typeof admissionEditSchema>

function AdmissionEditDialog({
  admission,
  open,
  onOpenChange,
}: {
  admission: Admission | null
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const queryClient = useQueryClient()
  const [classId, setClassId] = useState('')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const classesQuery = useQuery({
    queryKey: ['classes', 'admission-edit-options'],
    queryFn: () => schoolApi.classes.list(
      { page: 1, limit: 100, sort_by: 'name', sort_order: 'asc' },
      { status: 'active' },
    ),
    enabled: open,
  })
  const classOptions = classesQuery.data?.items ?? []
  const academicYears = [...new Set([
    ...classOptions.map((item) => item.academic_year),
    admission?.academic_year ?? '',
  ].filter(Boolean))].sort().reverse()
  const sections = [...new Set([
    ...classOptions.map((item) => item.section ?? ''),
    admission?.section ?? '',
  ])].sort()
  const form = useForm<AdmissionEditValues>({
    resolver: zodResolver(admissionEditSchema),
    defaultValues: admission ? {
      academic_year: admission.academic_year,
      section: admission.section ?? '',
      permanent_address: admission.permanent_address ?? '',
      temporary_address: admission.temporary_address ?? '',
      nationality: admission.nationality ?? '',
      disability: admission.disability ?? '',
      blood_group: admission.blood_group ?? '',
      reason_for_school_change: admission.reason_for_school_change ?? '',
      notes: admission.notes ?? '',
    } : {
      academic_year: '',
      section: '',
      permanent_address: '',
      temporary_address: '',
      nationality: '',
      disability: '',
      blood_group: '',
      reason_for_school_change: '',
      notes: '',
    },
  })
  const mutation = useMutation({
    mutationFn: (values: AdmissionEditValues) => {
      if (!admission) throw new Error('Select an admission before saving.')
      return admissionsApi.admissions.update(admission.id, {
        ...values,
        ...(classId ? { class_id: Number(classId) } : {}),
      })
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['admissions'] }),
        queryClient.invalidateQueries({ queryKey: ['admissions', admission?.id] }),
      ])
      onOpenChange(false)
    },
    onError: (error) => setErrorMessage(toApiError(error).message),
  })
  return (
    <FormDialog
      description="The API allows updates until an application is approved or rejected. The server validates allowed fields and workflow rules."
      onOpenChange={onOpenChange}
      open={open}
      title={`Edit admission${admission ? ` — ${admission.admission_code}` : ''}`}
    >
      {errorMessage ? <ErrorState title="Admission was not updated" description={errorMessage} /> : null}
      {classesQuery.error ? (
        <ErrorState description={toApiError(classesQuery.error).message} onRetry={() => void classesQuery.refetch()} />
      ) : (
        <ClassRecordSelector
          classes={classesQuery.data?.items ?? []}
          initialClassId={admission?.class_id}
          labelPrefix="Target active class"
          onChange={(_, schoolClass) => setClassId(schoolClass ? String(schoolClass.id) : '')}
        />
      )}
      <form className="mt-4 grid gap-4 sm:grid-cols-2" noValidate onSubmit={form.handleSubmit((values) => {
        setErrorMessage(null)
        mutation.mutate(values)
      })}>
        <FormField error={form.formState.errors.academic_year?.message} label="Academic year" required>
          {({ id, describedBy }) => (
            <select id={id} aria-describedby={describedBy} className="h-10 rounded-lg border border-input bg-white px-3 text-sm" {...form.register('academic_year')}>
              <option value="">Select an academic year</option>
              {academicYears.map((year) => <option key={year} value={year}>{year}</option>)}
            </select>
          )}
        </FormField>
        <FormField error={form.formState.errors.section?.message} label="Section">
          {({ id, describedBy }) => (
            <select id={id} aria-describedby={describedBy} className="h-10 rounded-lg border border-input bg-white px-3 text-sm" {...form.register('section')}>
              <option value="">Not specified</option>
              {sections.filter(Boolean).map((section) => <option key={section} value={section}>{section}</option>)}
            </select>
          )}
        </FormField>
        <FormField label="Permanent address">
          {({ id }) => <Input id={id} {...form.register('permanent_address')} />}
        </FormField>
        <FormField label="Temporary address">
          {({ id }) => <Input id={id} {...form.register('temporary_address')} />}
        </FormField>
        <FormField label="Nationality">
          {({ id }) => <Input id={id} {...form.register('nationality')} />}
        </FormField>
        <FormField label="Blood group">
          {({ id }) => <Input id={id} {...form.register('blood_group')} />}
        </FormField>
        <FormField label="Disability/support information">
          {({ id }) => <Input id={id} {...form.register('disability')} />}
        </FormField>
        <FormField label="Reason for school change">
          {({ id }) => <Input id={id} {...form.register('reason_for_school_change')} />}
        </FormField>
        <FormField label="Application notes">
          {({ id }) => <Input id={id} {...form.register('notes')} />}
        </FormField>
        <div className="flex justify-end gap-2 sm:col-span-2">
          <Button onClick={() => onOpenChange(false)} type="button" variant="outline">Cancel</Button>
          <Button disabled={mutation.isPending} type="submit">{mutation.isPending ? 'Saving…' : 'Save application'}</Button>
        </div>
      </form>
    </FormDialog>
  )
}

function AdmissionRejectionDialog({
  admission,
  open,
  onOpenChange,
}: {
  admission: Admission | null
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const queryClient = useQueryClient()
  const [reason, setReason] = useState('')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const mutation = useMutation({
    mutationFn: () => {
      if (!admission || reason.trim().length < 3) throw new Error('Enter a rejection reason of at least 3 characters.')
      return admissionsApi.admissions.reject(admission.id, reason.trim())
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['admissions'] }),
        queryClient.invalidateQueries({ queryKey: ['admissions', admission?.id] }),
      ])
      onOpenChange(false)
      setReason('')
    },
    onError: (error) => setErrorMessage(toApiError(error).message),
  })
  return (
    <FormDialog
      description="The rejection reason is shown to the parent and is recorded as a workflow status change."
      onOpenChange={onOpenChange}
      open={open}
      title={`Reject admission${admission ? ` — ${admission.admission_code}` : ''}`}
    >
      {errorMessage ? <ErrorState title="Admission was not rejected" description={errorMessage} /> : null}
      <label className="grid gap-2 text-sm font-medium" htmlFor="admission-rejection-reason">Rejection reason</label>
      <textarea className="min-h-24 rounded-lg border border-input bg-white p-3 text-sm" id="admission-rejection-reason" onChange={(event) => setReason(event.target.value)} value={reason} />
      <div className="flex justify-end gap-2">
        <Button onClick={() => onOpenChange(false)} type="button" variant="outline">Cancel</Button>
        <Button disabled={reason.trim().length < 3 || mutation.isPending} onClick={() => mutation.mutate()} variant="destructive">{mutation.isPending ? 'Rejecting…' : 'Reject admission'}</Button>
      </div>
    </FormDialog>
  )
}

function AdmissionDetailDialog({
  admissionId,
  open,
  onOpenChange,
  onEdit,
  onReject,
}: {
  admissionId: number | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onEdit: (admission: Admission) => void
  onReject: (admission: Admission) => void
}) {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [enrollmentSection, setEnrollmentSection] = useState('')
  const [enrollmentAcademicYear, setEnrollmentAcademicYear] = useState('')
  const [enrollmentDialogOpen, setEnrollmentDialogOpen] = useState(false)
  const enabled = open && admissionId !== null
  const admissionQuery = useQuery({
    queryKey: ['admissions', admissionId],
    queryFn: () => admissionsApi.admissions.get(admissionId!),
    enabled,
  })
  const admission = admissionQuery.data
  const canEnroll = user?.permissions?.includes('enrollment.create') ?? false
  const canReadClasses = user?.permissions?.includes('classes.read') ?? false
  const enrollmentClassesQuery = useQuery({
    queryKey: ['classes', 'enrollment-options', admission?.id, admission?.class_name],
    queryFn: () => schoolApi.classes.list(
      { page: 1, limit: 100, sort_by: 'name', sort_order: 'asc' },
      { status: 'active' },
    ),
    enabled: enabled && admission?.status === 'approved' && canEnroll && canReadClasses,
  })
  const gradeClasses = enrollmentClassesQuery.data?.items.filter((item) => (
    item.name === admission?.class_name
  )) ?? []
  const enrollmentYears = [...new Set(gradeClasses.map((item) => item.academic_year))].sort().reverse()
  const enrollmentSections = [...new Set(gradeClasses
    .filter((item) => item.academic_year === enrollmentAcademicYear)
    .map((item) => item.section)
    .filter((section): section is string => Boolean(section)))].sort()
  const selectedEnrollmentClass = gradeClasses.find((item) => (
    item.section === enrollmentSection && item.academic_year === enrollmentAcademicYear
  ))
  const canReadInquiry = user?.permissions?.includes('inquiries.read') ?? false
  const inquiryQuery = useQuery({
    queryKey: ['inquiries', admission?.inquiry_id],
    queryFn: () => admissionsApi.inquiries.get(admission!.inquiry_id),
    enabled: enabled && canReadInquiry && admission !== undefined,
  })
  const approvalMutation = useMutation({
    mutationFn: () => {
      if (admissionId === null) throw new Error('Select an admission first.')
      return admissionsApi.admissions.approve(admissionId)
    },
    onSuccess: async () => {
      setSuccessMessage('Admission approved and ready for enrollment.')
      setErrorMessage(null)
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['admissions'] }),
        queryClient.invalidateQueries({ queryKey: ['admissions', admissionId] }),
        queryClient.invalidateQueries({ queryKey: ['inquiries'] }),
      ])
    },
    onError: (error) => setErrorMessage(toApiError(error).message),
  })
  const enrollmentMutation = useMutation({
    mutationFn: () => {
      if (admissionId === null) throw new Error('Select an admission first.')
      if (!selectedEnrollmentClass) throw new Error('Select a section and academic year for enrollment.')
      return admissionsApi.admissions.enroll(admissionId, selectedEnrollmentClass.id)
    },
    onSuccess: async (result) => {
      setSuccessMessage(`Enrolled ${result.student_code}; roll number ${result.roll_number}.`)
      setErrorMessage(null)
      setEnrollmentDialogOpen(false)
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['admissions'] }),
        queryClient.invalidateQueries({ queryKey: ['admissions', admissionId] }),
        queryClient.invalidateQueries({ queryKey: ['students'] }),
        queryClient.invalidateQueries({ queryKey: ['inquiries'] }),
      ])
    },
    onError: (error) => setErrorMessage(toApiError(error).message),
  })
  const documentsVerified = admission !== undefined
    && REQUIRED_ADMISSION_DOCUMENT_TYPES.every((type) => admission.documents.some((document) => document.document_type === type && document.verification_status === 'VERIFIED'))
  const canUpdate = user?.permissions?.includes('admissions.update') ?? false
  const canApprove = user?.permissions?.includes('admissions.approve') ?? false
  const canReject = user?.permissions?.includes('admissions.reject') ?? false
  const isClosed = admission?.status === 'approved' || admission?.status === 'rejected'

  return (
    <Dialog onOpenChange={onOpenChange} open={open}>
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-3xl">
        <DialogHeader>
          <DialogTitle>Admission details{admission ? ` — ${admission.admission_code}` : ''}</DialogTitle>
          <DialogDescription>Review application data, required documents, and the available approval/enrollment operations.</DialogDescription>
        </DialogHeader>
        {admissionQuery.isLoading ? <LoadingState label="Loading admission" /> : null}
        {admissionQuery.error ? <ErrorState description={toApiError(admissionQuery.error).message} onRetry={() => void admissionQuery.refetch()} /> : null}
        {successMessage ? <SuccessState title="Admission workflow updated" description={successMessage} /> : null}
        {errorMessage ? <ErrorState title="Admission operation failed" description={errorMessage} /> : null}
        {admission ? (
          <div className="grid gap-5">
            <section className="grid gap-2 rounded-lg border border-slate-200 p-4 sm:grid-cols-2">
              <p><strong>Status:</strong> {admission.status}</p>
              <p><strong>Inquiry ID:</strong> {admission.inquiry_id}</p>
              <p><strong>Class:</strong> {admission.class_name ?? `Class ${admission.class_id}`}</p>
              <p><strong>Section:</strong> {admission.section ?? 'Assigned during enrollment'}</p>
              <p><strong>Academic year:</strong> {admission.academic_year} <span className="text-xs text-slate-500">(finalized during enrollment)</span></p>
              <p><strong>Student ID:</strong> {admission.student_id ?? 'Not enrolled'}</p>
              <p><strong>Student Aadhaar:</strong> {admission.student_aadhaar_masked ?? 'Not provided'}</p>
              <p><strong>Parent Aadhaar:</strong> {admission.parent_aadhaar_masked ?? 'Not provided'}</p>
              <p><strong>Previous-school marks:</strong> {admission.last_school_marks ?? 'Not provided'}</p>
              <p><strong>Previous-school percentage:</strong> {admission.last_school_percentage == null ? 'Not provided' : `${admission.last_school_percentage}%`}</p>
              <p><strong>Previous-school ID / roll number:</strong> {admission.last_school_id_or_roll_number ?? 'Not provided'}</p>
              {admission.rejection_reason ? <p className="text-destructive sm:col-span-2"><strong>Rejection reason:</strong> {admission.rejection_reason}</p> : null}
            </section>
            {canReadInquiry ? inquiryQuery.error ? (
              <ErrorState description={toApiError(inquiryQuery.error).message} onRetry={() => void inquiryQuery.refetch()} />
            ) : inquiryQuery.data ? (
              <section className="rounded-lg border border-slate-200 p-4">
                <h3 className="text-sm font-semibold">Applicant</h3>
                <p className="mt-1 text-sm">{inquiryQuery.data.inquiry_code} · {inquiryQuery.data.first_name} {inquiryQuery.data.last_name}</p>
                <p className="text-sm text-slate-600">{inquiryQuery.data.email} · {inquiryQuery.data.parent_mobile}</p>
              </section>
            ) : null : (
              <p className="text-sm text-slate-500">Applicant information requires the inquiries.read permission.</p>
            )}
            {canUpdate && !isClosed ? <Button onClick={() => onEdit(admission)} type="button" variant="outline">Edit application</Button> : null}
            <AdmissionDocumentsPanel admission={admission} />
            <div className="flex flex-wrap gap-2">
              {canApprove && admission.status === 'document_verification' ? (
                <Button disabled={approvalMutation.isPending || !documentsVerified} onClick={() => approvalMutation.mutate()}>
                  {approvalMutation.isPending ? 'Approving…' : 'Approve for enrollment'}
                </Button>
              ) : null}
              {canReject && !isClosed ? <Button onClick={() => onReject(admission)} variant="destructive">Reject admission</Button> : null}
              {canEnroll && admission.status === 'approved' && admission.student_id === null ? (
                <>
                  <Button
                    disabled={!documentsVerified || enrollmentMutation.isPending}
                    onClick={() => {
                      setEnrollmentSection('')
                      setEnrollmentAcademicYear('')
                      setEnrollmentDialogOpen(true)
                    }}
                    type="button"
                    variant="outline"
                  >
                    Enroll student
                  </Button>
                  <Dialog onOpenChange={setEnrollmentDialogOpen} open={enrollmentDialogOpen}>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Assign section for enrollment</DialogTitle>
                        <DialogDescription>
                          Choose the section and academic year for {admission.class_name ?? 'the requested class'}. The parent did not select these; school staff assign them during enrollment.
                        </DialogDescription>
                      </DialogHeader>
                      {!canReadClasses ? (
                        <ErrorState description="Class-viewing permission is required to assign an enrollment section." />
                      ) : enrollmentClassesQuery.isLoading ? <LoadingState label="Loading available sections" /> : enrollmentClassesQuery.error ? (
                        <ErrorState description={toApiError(enrollmentClassesQuery.error).message} onRetry={() => void enrollmentClassesQuery.refetch()} />
                      ) : gradeClasses.length ? (
                        <div className="grid gap-3 sm:grid-cols-2">
                          <label className="grid gap-2 text-sm font-medium">
                            Academic year
                            <select
                              className="h-10 w-full rounded-lg border border-input bg-white px-3 text-sm"
                              onChange={(event) => {
                                setEnrollmentAcademicYear(event.target.value)
                                setEnrollmentSection('')
                              }}
                              value={enrollmentAcademicYear}
                            >
                              <option value="">Select an academic year</option>
                              {enrollmentYears.map((year) => (
                                <option key={year} value={year}>{year}</option>
                              ))}
                            </select>
                          </label>
                          <label className="grid gap-2 text-sm font-medium">
                            Section
                            <select
                              className="h-10 w-full rounded-lg border border-input bg-white px-3 text-sm"
                              disabled={!enrollmentAcademicYear}
                              onChange={(event) => setEnrollmentSection(event.target.value)}
                              value={enrollmentSection}
                            >
                              <option value="">Select a section</option>
                              {enrollmentSections.map((section) => (
                                <option key={section} value={section}>{section}</option>
                              ))}
                            </select>
                          </label>
                        </div>
                      ) : <p className="text-sm text-amber-800">No active classes are available for this grade.</p>}
                      {enrollmentMutation.error ? <ErrorState title="Enrollment failed" description={toApiError(enrollmentMutation.error).message} /> : null}
                      <DialogFooter>
                        <Button onClick={() => setEnrollmentDialogOpen(false)} type="button" variant="outline">
                          Cancel
                        </Button>
                        <Button
                          disabled={!selectedEnrollmentClass || enrollmentMutation.isPending || !documentsVerified}
                          onClick={() => enrollmentMutation.mutate()}
                          type="button"
                        >
                          {enrollmentMutation.isPending ? 'Enrolling…' : 'Confirm enrollment'}
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                </>
              ) : null}
            </div>
            {canApprove && admission.status === 'document_verification' && !documentsVerified ? (
              <Alert>
                <AlertTitle>Approval prerequisites incomplete</AlertTitle>
                <AlertDescription>Every required document must be uploaded and verified before approval.</AlertDescription>
              </Alert>
            ) : null}
          </div>
        ) : null}
      </DialogContent>
    </Dialog>
  )
}

export function AdmissionsPage() {
  const [status, setStatus] = useState<Admission['status'] | ''>('')
  const [academicYear, setAcademicYear] = useState('')
  const [page, setPage] = useState(1)
  const [selectedAdmissionId, setSelectedAdmissionId] = useState<number | null>(null)
  const [editingAdmission, setEditingAdmission] = useState<Admission | null>(null)
  const [rejectingAdmission, setRejectingAdmission] = useState<Admission | null>(null)
  const query = useQuery({
    queryKey: ['admissions', { status, academicYear, page }],
    queryFn: () => admissionsApi.admissions.list(
      { page, limit: pageSize, sort_by: 'id', sort_order: 'desc' },
      { status: status || undefined, academic_year: academicYear || undefined },
    ),
  })
  const columns = [
    { id: 'code', header: 'Admission code', cell: (item: Admission) => <span className="font-semibold">{item.admission_code}</span> },
    { id: 'inquiry', header: 'Inquiry ID', cell: (item: Admission) => item.inquiry_id },
    { id: 'class', header: 'Class ID', cell: (item: Admission) => item.class_id },
    { id: 'year', header: 'Academic year', cell: (item: Admission) => item.academic_year },
    { id: 'status', header: 'Status', cell: (item: Admission) => item.status },
    { id: 'documents', header: 'Documents', cell: (item: Admission) => `${item.documents.length} uploaded` },
    { id: 'actions', header: 'Actions', cell: (item: Admission) => (
      <Button onClick={() => setSelectedAdmissionId(item.id)} size="sm" variant="outline">Review</Button>
    ) },
  ]

  return (
    <>
      <PageHeader description="Review inquiry-linked applications, maintain editable application fields, verify documents, approve eligible applications, and enroll students." title="Admissions" />
      <RecordList
        columns={columns}
        emptyMessage="No admission applications match these filters."
        error={query.error ? toApiError(query.error).message : undefined}
        getRowId={(item) => item.id}
        isLoading={query.isLoading}
        onPageChange={setPage}
        onRetry={() => void query.refetch()}
        pagination={query.data?.pagination}
        rows={query.data?.items ?? []}
        toolbar={
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="grid gap-2 text-sm font-medium" htmlFor="admission-status-filter">
              Filter by status
              <select className="h-10 rounded-lg border border-input bg-white px-3 text-sm" id="admission-status-filter" onChange={(event) => { setStatus(event.target.value as Admission['status'] | ''); setPage(1) }} value={status}>
                <option value="">All statuses</option>
                {admissionStatuses.map((item) => <option key={item} value={item}>{item}</option>)}
              </select>
            </label>
            <label className="grid gap-2 text-sm font-medium" htmlFor="admission-year-filter">
              Academic year
              <Input id="admission-year-filter" onChange={(event) => { setAcademicYear(event.target.value); setPage(1) }} placeholder="Filter academic year" value={academicYear} />
            </label>
          </div>
        }
      />
      <AdmissionDetailDialog
        admissionId={selectedAdmissionId}
        onEdit={(admission) => setEditingAdmission(admission)}
        onOpenChange={(open) => {
          if (!open) setSelectedAdmissionId(null)
        }}
        onReject={(admission) => setRejectingAdmission(admission)}
        open={selectedAdmissionId !== null}
      />
      <AdmissionEditDialog
        key={editingAdmission?.id ?? 'no-admission'}
        admission={editingAdmission}
        onOpenChange={(open) => {
          if (!open) setEditingAdmission(null)
        }}
        open={editingAdmission !== null}
      />
      <AdmissionRejectionDialog
        admission={rejectingAdmission}
        onOpenChange={(open) => {
          if (!open) setRejectingAdmission(null)
        }}
        open={rejectingAdmission !== null}
      />
    </>
  )
}

export function DocumentsPage() {
  const [status, setStatus] = useState<Admission['status'] | ''>('')
  const [academicYear, setAcademicYear] = useState('')
  const [page, setPage] = useState(1)
  const [selectedAdmissionId, setSelectedAdmissionId] = useState<number | null>(null)
  const query = useQuery({
    queryKey: ['admissions', 'documents', { status, academicYear, page }],
    queryFn: () => admissionsApi.admissions.list(
      { page, limit: pageSize, sort_by: 'id', sort_order: 'desc' },
      { status: status || undefined, academic_year: academicYear || undefined },
    ),
  })
  const selectedAdmissionQuery = useQuery({
    queryKey: ['admissions', selectedAdmissionId],
    queryFn: () => admissionsApi.admissions.get(selectedAdmissionId!),
    enabled: selectedAdmissionId !== null,
  })
  const columns = [
    { id: 'code', header: 'Admission code', cell: (item: Admission) => item.admission_code },
    { id: 'status', header: 'Application status', cell: (item: Admission) => item.status },
    { id: 'documents', header: 'Uploaded', cell: (item: Admission) => `${item.documents.length} document records` },
    { id: 'actions', header: 'Actions', cell: (item: Admission) => (
      <Button onClick={() => setSelectedAdmissionId(item.id)} size="sm" variant="outline">Manage documents</Button>
    ) },
  ]
  return (
    <>
      <PageHeader
        description="Review documents submitted by parents. Staff can view, verify, or reject each file; parents upload or replace documents from the admission portal."
        title="Documents"
      />
      <RecordList
        columns={columns}
        emptyMessage="No admission applications match these filters."
        error={query.error ? toApiError(query.error).message : undefined}
        getRowId={(item) => item.id}
        isLoading={query.isLoading}
        onPageChange={setPage}
        onRetry={() => void query.refetch()}
        pagination={query.data?.pagination}
        rows={query.data?.items ?? []}
        toolbar={
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="grid gap-2 text-sm font-medium" htmlFor="documents-status-filter">
              Filter by application status
              <select className="h-10 rounded-lg border border-input bg-white px-3 text-sm" id="documents-status-filter" onChange={(event) => { setStatus(event.target.value as Admission['status'] | ''); setPage(1) }} value={status}>
                <option value="">All statuses</option>
                {admissionStatuses.map((item) => <option key={item} value={item}>{item}</option>)}
              </select>
            </label>
            <label className="grid gap-2 text-sm font-medium" htmlFor="documents-year-filter">
              Academic year
              <Input id="documents-year-filter" onChange={(event) => { setAcademicYear(event.target.value); setPage(1) }} placeholder="Filter academic year" value={academicYear} />
            </label>
          </div>
        }
      />
      <div className="mt-5">
        {selectedAdmissionId === null ? <EmptyState title="Select an application" description="Choose an admission application to review its required documents." /> : null}
        {selectedAdmissionId !== null && selectedAdmissionQuery.isLoading ? <LoadingState label="Loading application documents" /> : null}
        {selectedAdmissionQuery.error ? <ErrorState description={toApiError(selectedAdmissionQuery.error).message} onRetry={() => void selectedAdmissionQuery.refetch()} /> : null}
        {selectedAdmissionQuery.data ? (
          <section className="grid gap-4 rounded-xl border border-slate-200 bg-white p-4">
            <div>
              <h2 className="font-semibold">{selectedAdmissionQuery.data.admission_code}</h2>
              <p className="text-sm text-slate-600">Application status: {selectedAdmissionQuery.data.status}</p>
            </div>
            <AdmissionDocumentsPanel admission={selectedAdmissionQuery.data} />
          </section>
        ) : null}
      </div>
    </>
  )
}
