import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useLocation } from 'react-router-dom'
import { z } from 'zod'
import { PermissionGate } from '@/components/auth/permission-gate'
import { FormDialog } from '@/components/school/form-dialog'
import { RecordList } from '@/components/school/record-list'
import { Button } from '@/components/ui/button'
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/async-state'
import { FormField } from '@/components/ui/form-field'
import { Input } from '@/components/ui/input'
import { PageHeader } from '@/components/ui/page-header'
import { SearchField } from '@/components/ui/search-field'
import { admissionsApi, type Inquiry, type InquiryStatus, type Interview } from '@/features/admissions/admissions-api'
import { schoolApi } from '@/features/school/school-api'
import { toApiError } from '@/lib/api/api-error'
import { useAuth } from '@/features/auth/auth-context'

const pageSize = 10
const statusOptions: InquiryStatus[] = [
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

const scheduleSchema = z.object({
  schedule_date: z.string().min(1),
  schedule_time: z.string().min(1),
  location: z.string().trim().min(1).max(255),
  mode: z.enum(['ONLINE', 'OFFLINE']),
  remarks: z.string().optional(),
})
type ScheduleValues = z.infer<typeof scheduleSchema>

function ScheduleInterviewDialog({
  inquiry,
  open,
  onOpenChange,
}: {
  inquiry: Inquiry | null
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [teacherId, setTeacherId] = useState('')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const canReadTeachers = user?.permissions?.includes('teachers.read') ?? false
  const teachersQuery = useQuery({
    queryKey: ['teachers', 'interviewer-options'],
    queryFn: () => schoolApi.teachers.list(
      { page: 1, limit: 100, sort_by: 'first_name', sort_order: 'asc' },
      { status: 'active' },
    ),
    enabled: open && canReadTeachers,
  })
  const form = useForm<ScheduleValues>({
    resolver: zodResolver(scheduleSchema),
    defaultValues: { schedule_date: '', schedule_time: '', location: '', mode: 'OFFLINE', remarks: '' },
  })
  const mutation = useMutation({
    mutationFn: (values: ScheduleValues) => {
      if (!inquiry) throw new Error('Select an inquiry before scheduling.')
      return admissionsApi.interviews.schedule(inquiry.id, {
        ...values,
        remarks: values.remarks || undefined,
        ...(teacherId ? { interviewer_teacher_id: Number(teacherId) } : {}),
      })
    },
    onSuccess: async () => {
      if (!inquiry) return
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['interviews', inquiry.id] }),
        queryClient.invalidateQueries({ queryKey: ['inquiries'] }),
        queryClient.invalidateQueries({ queryKey: ['inquiries', inquiry.id] }),
      ])
      form.reset()
      setTeacherId('')
      setErrorMessage(null)
      onOpenChange(false)
    },
    onError: (error) => setErrorMessage(toApiError(error).message),
  })
  return (
    <FormDialog
      description="Scheduling is allowed for inquiries in PROCESSING or INTERVIEW_SCHEDULED; the API records SCHEDULED and updates the inquiry workflow."
      onOpenChange={onOpenChange}
      open={open}
      title={inquiry ? `Schedule interview — ${inquiry.inquiry_code}` : 'Schedule interview'}
    >
      {errorMessage ? <ErrorState title="Interview was not scheduled" description={errorMessage} /> : null}
      <form className="grid gap-4 sm:grid-cols-2" noValidate onSubmit={form.handleSubmit((values) => {
        setErrorMessage(null)
        mutation.mutate(values)
      })}>
        <FormField error={form.formState.errors.schedule_date?.message} label="Interview date" required>
          {({ id, describedBy }) => <Input id={id} type="date" aria-describedby={describedBy} {...form.register('schedule_date')} />}
        </FormField>
        <FormField error={form.formState.errors.schedule_time?.message} label="Interview start time" required>
          {({ id, describedBy }) => <Input id={id} type="time" aria-describedby={describedBy} {...form.register('schedule_time')} />}
        </FormField>
        <FormField error={form.formState.errors.location?.message} label="Location or meeting details" required>
          {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('location')} />}
        </FormField>
        <FormField label="Mode" required>
          {({ id }) => (
            <select className="h-10 rounded-lg border border-input bg-white px-3 text-sm" id={id} {...form.register('mode')}>
              <option value="OFFLINE">Offline</option><option value="ONLINE">Online</option>
            </select>
          )}
        </FormField>
        <FormField label="Scheduling notes">
          {({ id }) => <Input id={id} {...form.register('remarks')} />}
        </FormField>
        {canReadTeachers ? teachersQuery.error ? (
          <p className="text-sm text-destructive sm:col-span-2">Interviewer list unavailable: {toApiError(teachersQuery.error).message} You may still schedule without an assigned interviewer.</p>
        ) : (
          <label className="grid gap-2 text-sm font-medium">
            Optional interviewer
            <select className="h-10 rounded-lg border border-input bg-white px-3 text-sm" onChange={(event) => setTeacherId(event.target.value)} value={teacherId}>
              <option value="">No interviewer assigned</option>
              {(teachersQuery.data?.items ?? []).map((teacher) => (
                <option key={teacher.id} value={teacher.id}>{teacher.first_name} {teacher.last_name} · {teacher.employee_no}</option>
              ))}
            </select>
          </label>
        ) : null}
        <div className="flex justify-end gap-2 sm:col-span-2">
          <Button onClick={() => onOpenChange(false)} type="button" variant="outline">Cancel</Button>
          <Button disabled={mutation.isPending} type="submit">{mutation.isPending ? 'Scheduling…' : 'Schedule interview'}</Button>
        </div>
      </form>
    </FormDialog>
  )
}

function InterviewResultDialog({
  interview,
  open,
  onOpenChange,
}: {
  interview: Interview | null
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const queryClient = useQueryClient()
  const [result, setResult] = useState<'PASSED' | 'FAILED' | 'ABSENT'>('PASSED')
  const [remarks, setRemarks] = useState('')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const mutation = useMutation({
    mutationFn: () => {
      if (!interview) throw new Error('Select an interview before recording a result.')
      return admissionsApi.interviews.recordResult(interview.id, result, remarks || undefined)
    },
    onSuccess: async () => {
      if (!interview) return
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['interviews', interview.inquiry_id] }),
        queryClient.invalidateQueries({ queryKey: ['interviews', interview.id] }),
        queryClient.invalidateQueries({ queryKey: ['inquiries'] }),
        queryClient.invalidateQueries({ queryKey: ['inquiries', interview.inquiry_id] }),
      ])
      setErrorMessage(null)
      onOpenChange(false)
    },
    onError: (error) => setErrorMessage(toApiError(error).message),
  })
  return (
    <FormDialog
      description="Only a scheduled interview can receive one result. Passed advances to INTERVIEW_PASS; failed or absent advances to INTERVIEW_FAIL."
      onOpenChange={onOpenChange}
      open={open}
      title="Record interview result"
    >
      {errorMessage ? <ErrorState title="Result was not recorded" description={errorMessage} /> : null}
      <label className="grid gap-2 text-sm font-medium" htmlFor="interview-result">Result</label>
      <select className="h-10 rounded-lg border border-input bg-white px-3 text-sm" id="interview-result" onChange={(event) => setResult(event.target.value as typeof result)} value={result}>
        <option value="PASSED">Passed</option><option value="FAILED">Failed</option><option value="ABSENT">Absent</option>
      </select>
      <label className="grid gap-2 text-sm font-medium" htmlFor="interview-result-remarks">Outcome notes</label>
      <textarea className="min-h-20 rounded-lg border border-input bg-white p-3 text-sm" id="interview-result-remarks" onChange={(event) => setRemarks(event.target.value)} value={remarks} />
      <div className="flex justify-end gap-2">
        <Button onClick={() => onOpenChange(false)} type="button" variant="outline">Cancel</Button>
        <Button disabled={mutation.isPending || !interview} onClick={() => mutation.mutate()}>{mutation.isPending ? 'Saving…' : 'Save result'}</Button>
      </div>
    </FormDialog>
  )
}

export function InterviewsPage() {
  const location = useLocation()
  const navigationState = location.state as { inquiryId?: number } | null
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<InquiryStatus | ''>('')
  const [page, setPage] = useState(1)
  const [selectedInquiryId, setSelectedInquiryId] = useState<number | null>(navigationState?.inquiryId ?? null)
  const [scheduling, setScheduling] = useState(false)
  const [resultInterview, setResultInterview] = useState<Interview | null>(null)
  const query = useQuery({
    queryKey: ['inquiries', 'interviews-select', { search, status, page }],
    queryFn: () => admissionsApi.inquiries.list(
      { page, limit: pageSize, sort_by: 'created_at', sort_order: 'desc' },
      { search: search || undefined, status: status || undefined },
    ),
  })
  const selectedInquiryQuery = useQuery({
    queryKey: ['inquiries', selectedInquiryId],
    queryFn: () => admissionsApi.inquiries.get(selectedInquiryId!),
    enabled: selectedInquiryId !== null,
  })
  const interviewsQuery = useQuery({
    queryKey: ['interviews', selectedInquiryId],
    queryFn: () => admissionsApi.interviews.listForInquiry(selectedInquiryId!),
    enabled: selectedInquiryId !== null,
  })
  const inquiry = selectedInquiryQuery.data
  const canSchedule = inquiry && (inquiry.status === 'PROCESSING' || inquiry.status === 'INTERVIEW_SCHEDULED')
  const columns = [
    { id: 'code', header: 'Inquiry code', cell: (item: Inquiry) => item.inquiry_code },
    { id: 'student', header: 'Student', cell: (item: Inquiry) => `${item.first_name} ${item.last_name}` },
    { id: 'class', header: 'Grade / class', cell: (item: Inquiry) => item.admission_for_class || 'Not specified' },
    { id: 'status', header: 'Inquiry status', cell: (item: Inquiry) => item.status },
    { id: 'action', header: 'Interviews', cell: (item: Inquiry) => (
      <Button onClick={() => setSelectedInquiryId(item.id)} size="sm" variant="outline">
        {selectedInquiryId === item.id ? 'Selected' : 'View interviews'}
      </Button>
    ) },
  ]

  return (
    <>
      <PageHeader
        description="The API lists interviews by inquiry rather than exposing a global interview list. Select an inquiry to view and manage its interview schedule."
        title="Interviews"
      />
      <RecordList
        caption="Inquiries available for interview"
        columns={columns}
        emptyMessage="No inquiries match these filters."
        error={query.error ? toApiError(query.error).message : undefined}
        getRowId={(item) => item.id}
        isLoading={query.isLoading}
        onPageChange={setPage}
        onRetry={() => void query.refetch()}
        pagination={query.data?.pagination}
        rows={query.data?.items ?? []}
        toolbar={
          <div className="grid min-w-0 items-end gap-3 sm:grid-cols-2">
            <SearchField label="Search inquiries" onChange={(value) => { setSearch(value); setPage(1) }} placeholder="Search name, code, email, or mobile" showLabel value={search} />
            <label className="grid min-w-0 gap-2 text-sm font-medium" htmlFor="interview-inquiry-status">
              Filter inquiries by status
              <select className="h-10 w-full min-w-0 rounded-lg border border-input bg-white px-3 text-sm" id="interview-inquiry-status" onChange={(event) => { setStatus(event.target.value as InquiryStatus | ''); setPage(1) }} value={status}>
                <option value="">All statuses</option>
                {statusOptions.map((item) => <option key={item} value={item}>{item}</option>)}
              </select>
            </label>
          </div>
        }
      />
      <section className="mt-6 grid gap-4">
        {selectedInquiryId === null ? (
          <EmptyState title="Select an inquiry" description="Choose an inquiry above to load its interview records." />
        ) : selectedInquiryQuery.isLoading ? <LoadingState label="Loading selected inquiry" /> : selectedInquiryQuery.error ? (
          <ErrorState description={toApiError(selectedInquiryQuery.error).message} onRetry={() => void selectedInquiryQuery.refetch()} />
        ) : inquiry ? (
          <>
            <div className="flex flex-wrap items-end justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold">{inquiry.inquiry_code} · {inquiry.first_name} {inquiry.last_name}</h2>
                <p className="text-sm text-slate-600">Inquiry status: {inquiry.status}</p>
              </div>
              <PermissionGate anyOf={['interviews.schedule']}>
                {canSchedule ? <Button onClick={() => setScheduling(true)}>Schedule interview</Button> : null}
              </PermissionGate>
            </div>
            {interviewsQuery.isLoading ? <LoadingState label="Loading interviews" /> : null}
            {interviewsQuery.error ? <ErrorState description={toApiError(interviewsQuery.error).message} onRetry={() => void interviewsQuery.refetch()} /> : null}
            {interviewsQuery.data?.length ? (
              <div className="grid gap-3">
                {interviewsQuery.data.map((interview) => (
                  <article className="grid gap-2 rounded-xl border border-slate-200 bg-white p-4 sm:grid-cols-[1fr_auto]" key={interview.id}>
                    <div className="grid gap-1 text-sm">
                      <h3 className="font-semibold">{interview.schedule_date} at {interview.schedule_time} · {interview.mode}</h3>
                      <p>{interview.location}</p>
                      <p className="text-slate-600">Result: {interview.result}{interview.interviewer_teacher_id ? ` · Interviewer ID ${interview.interviewer_teacher_id}` : ''}</p>
                      {interview.remarks ? <p className="text-slate-600">Notes: {interview.remarks}</p> : null}
                    </div>
                    {interview.result === 'SCHEDULED' ? (
                      <PermissionGate anyOf={['interviews.update']}>
                        <Button onClick={() => setResultInterview(interview)} size="sm" variant="outline">Record result</Button>
                      </PermissionGate>
                    ) : null}
                  </article>
                ))}
              </div>
            ) : interviewsQuery.data ? <EmptyState title="No interviews scheduled" description="Schedule an interview when the inquiry is in PROCESSING or INTERVIEW_SCHEDULED." /> : null}
          </>
        ) : null}
      </section>
      <ScheduleInterviewDialog
        key={selectedInquiryId ?? 'no-inquiry'}
        inquiry={inquiry ?? null}
        onOpenChange={setScheduling}
        open={scheduling}
      />
      <InterviewResultDialog
        interview={resultInterview}
        onOpenChange={(open) => {
          if (!open) setResultInterview(null)
        }}
        open={resultInterview !== null}
      />
    </>
  )
}
