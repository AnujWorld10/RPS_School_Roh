import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { PermissionGate } from '@/components/auth/permission-gate'
import { ClassRecordSelector } from '@/components/school/class-record-selector'
import { FormDialog } from '@/components/school/form-dialog'
import { RecordList } from '@/components/school/record-list'
import { StatusBadge } from '@/components/school/status-badge'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { ErrorState, LoadingState, SuccessState } from '@/components/ui/async-state'
import { ConfirmDialog } from '@/components/ui/confirm-dialog'
import { FormField } from '@/components/ui/form-field'
import { Input } from '@/components/ui/input'
import { PageHeader } from '@/components/ui/page-header'
import { SearchField } from '@/components/ui/search-field'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { toApiError } from '@/lib/api/api-error'
import { useAuth } from '@/features/auth/auth-context'
import { schoolApi, type Student } from '@/features/school/school-api'

const pageSize = 10
const studentSchema = z.object({
  admission_no: z.string().trim().max(50),
  first_name: z.string().trim().min(1).max(100),
  last_name: z.string().trim().min(1).max(100),
  date_of_birth: z.string().min(1),
  gender: z.enum(['male', 'female', 'other']),
  email: z.union([z.literal(''), z.string().email()]),
  phone: z.string().trim().max(30),
})

type StudentFormValues = z.infer<typeof studentSchema>

const statusTransitions: Record<Student['status'], Student['status'][]> = {
  prospective: ['active', 'inactive'],
  active: ['inactive', 'graduated', 'transferred'],
  inactive: ['active'],
  graduated: [],
  transferred: [],
}

function StudentFormDialog({
  student,
  open,
  onOpenChange,
}: {
  student: Student | null
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const queryClient = useQueryClient()
  const [formError, setFormError] = useState<string | null>(null)
  const form = useForm<StudentFormValues>({
    resolver: zodResolver(studentSchema),
    defaultValues: student
      ? {
          admission_no: student.admission_no ?? '',
          first_name: student.first_name,
          last_name: student.last_name,
          date_of_birth: student.date_of_birth,
          gender: student.gender === 'female' || student.gender === 'other' ? student.gender : 'male',
          email: student.email ?? '',
          phone: student.phone ?? '',
        }
      : {
          admission_no: '',
          first_name: '',
          last_name: '',
          date_of_birth: '',
          gender: 'male',
          email: '',
          phone: '',
        },
  })
  const mutation = useMutation({
    mutationFn: (values: StudentFormValues) => {
      if (student) {
        return schoolApi.students.update(student.id, {
          first_name: values.first_name,
          last_name: values.last_name,
          date_of_birth: values.date_of_birth,
          gender: values.gender,
          email: values.email || null,
          phone: values.phone || null,
        })
      }

      return schoolApi.students.create({
        admission_no: values.admission_no || null,
        first_name: values.first_name,
        last_name: values.last_name,
        date_of_birth: values.date_of_birth,
        gender: values.gender,
        email: values.email || null,
        phone: values.phone || null,
      })
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['students'] })
      onOpenChange(false)
    },
    onError: (error) => setFormError(toApiError(error).message),
  })

  return (
    <FormDialog
      description={student
        ? 'Update profile fields supported by the student API. Enrollment status is managed separately.'
        : 'A student created without a class starts as prospective. Assign an active class from enrollment management.'}
      onOpenChange={onOpenChange}
      open={open}
      title={student ? 'Edit student' : 'Add student'}
    >
      {formError ? (
        <Alert className="mb-3" variant="destructive">
          <AlertTitle>Student could not be saved</AlertTitle>
          <AlertDescription>{formError}</AlertDescription>
        </Alert>
      ) : null}
      <form className="grid gap-4 sm:grid-cols-2" noValidate onSubmit={form.handleSubmit((values) => {
        setFormError(null)
        mutation.mutate(values)
      })}>
        {!student ? (
          <FormField error={form.formState.errors.admission_no?.message} label="Admission number">
            {({ id, describedBy }) => (
              <Input id={id} aria-describedby={describedBy} {...form.register('admission_no')} />
            )}
          </FormField>
        ) : null}
        <FormField error={form.formState.errors.first_name?.message} label="First name" required>
          {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('first_name')} />}
        </FormField>
        <FormField error={form.formState.errors.last_name?.message} label="Last name" required>
          {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('last_name')} />}
        </FormField>
        <FormField error={form.formState.errors.date_of_birth?.message} label="Date of birth" required>
          {({ id, describedBy }) => (
            <Input id={id} type="date" aria-describedby={describedBy} {...form.register('date_of_birth')} />
          )}
        </FormField>
        <FormField error={form.formState.errors.gender?.message} label="Gender" required>
          {({ id }) => (
            <select id={id} className="h-10 rounded-lg border border-input bg-white px-3 text-sm" {...form.register('gender')}>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          )}
        </FormField>
        <FormField error={form.formState.errors.email?.message} label="Student or guardian email">
          {({ id, describedBy }) => (
            <Input id={id} type="email" aria-describedby={describedBy} {...form.register('email')} />
          )}
        </FormField>
        <FormField error={form.formState.errors.phone?.message} label="Student or guardian phone">
          {({ id, describedBy }) => (
            <Input id={id} type="tel" aria-describedby={describedBy} {...form.register('phone')} />
          )}
        </FormField>
        <div className="flex justify-end gap-2 sm:col-span-2">
          <Button onClick={() => onOpenChange(false)} type="button" variant="outline">Cancel</Button>
          <Button disabled={mutation.isPending} type="submit">{mutation.isPending ? 'Saving…' : 'Save student'}</Button>
        </div>
      </form>
    </FormDialog>
  )
}

function StudentDetailsDialog({
  student,
  open,
  onOpenChange,
}: {
  student: Student | null
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const enabled = open && student !== null
  const detailQuery = useQuery({
    queryKey: ['students', student?.id, 'detail'],
    queryFn: () => schoolApi.students.get(student!.id),
    enabled,
  })
  const subjectsQuery = useQuery({
    queryKey: ['students', student?.id, 'subjects'],
    queryFn: () => schoolApi.students.listSubjects(student!.id),
    enabled,
  })
  const detail = detailQuery.data

  return (
    <Dialog onOpenChange={onOpenChange} open={open}>
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>Student details</DialogTitle>
          <DialogDescription>Profile and current-class subjects returned by the API.</DialogDescription>
        </DialogHeader>
        {detailQuery.isLoading ? <LoadingState label="Loading student details" /> : null}
        {detailQuery.error ? (
          <ErrorState description={toApiError(detailQuery.error).message} onRetry={() => void detailQuery.refetch()} />
        ) : null}
        {detail ? (
          <dl className="grid gap-3 rounded-lg border border-slate-200 p-4 sm:grid-cols-2">
            <div><dt className="text-xs text-slate-500">Name</dt><dd className="font-medium">{detail.first_name} {detail.last_name}</dd></div>
            <div><dt className="text-xs text-slate-500">Admission no.</dt><dd>{detail.admission_no ?? 'Not assigned'}</dd></div>
            <div><dt className="text-xs text-slate-500">Date of birth</dt><dd>{detail.date_of_birth}</dd></div>
            <div><dt className="text-xs text-slate-500">Gender</dt><dd>{detail.gender}</dd></div>
            <div><dt className="text-xs text-slate-500">Email</dt><dd>{detail.email ?? 'Not provided'}</dd></div>
            <div><dt className="text-xs text-slate-500">Phone</dt><dd>{detail.phone ?? 'Not provided'}</dd></div>
            <div><dt className="text-xs text-slate-500">Current class ID</dt><dd>{detail.current_class_id ?? 'Not assigned'}</dd></div>
            <div><dt className="text-xs text-slate-500">Status</dt><dd><StatusBadge status={detail.status} /></dd></div>
          </dl>
        ) : null}
        <section className="grid gap-2">
          <h3 className="text-sm font-semibold">Current class subjects</h3>
          {subjectsQuery.isLoading ? <LoadingState label="Loading class subjects" /> : null}
          {subjectsQuery.error ? (
            <ErrorState description={toApiError(subjectsQuery.error).message} onRetry={() => void subjectsQuery.refetch()} />
          ) : subjectsQuery.data?.length ? (
            <ul className="divide-y divide-slate-200 rounded-lg border border-slate-200">
              {subjectsQuery.data.map((subject) => (
                <li className="p-3 text-sm" key={subject.id}><strong>{subject.code}</strong> · {subject.name}</li>
              ))}
            </ul>
          ) : subjectsQuery.data ? (
            <p className="text-sm text-slate-500">No active class subjects are available.</p>
          ) : null}
        </section>
      </DialogContent>
    </Dialog>
  )
}

function StudentEnrollmentDialog({
  student,
  open,
  onOpenChange,
}: {
  student: Student | null
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [classId, setClassId] = useState('')
  const [nextStatus, setNextStatus] = useState<Student['status'] | ''>('')
  const [reason, setReason] = useState('')
  const [message, setMessage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const canReadClasses = user?.permissions?.includes('classes.read') ?? false
  const enabled = open && student !== null
  const studentQuery = useQuery({
    queryKey: ['students', student?.id, 'detail'],
    queryFn: () => schoolApi.students.get(student!.id),
    enabled,
  })
  const currentStudent = studentQuery.data ?? student
  const activeClassesQuery = useQuery({
    queryKey: ['classes', 'active-options'],
    queryFn: () => schoolApi.classes.list(
      { page: 1, limit: 100, sort_by: 'name', sort_order: 'asc' },
      { status: 'active' },
    ),
    enabled,
  })
  const assignClassMutation = useMutation({
    mutationFn: () => {
      const selectedClass = activeClassesQuery.data?.items.find((item) => item.id === Number(classId))
      if (!selectedClass || !student) {
        throw new Error('Select an active class before assigning enrollment.')
      }
      return schoolApi.students.assignClass(student.id, selectedClass.id, selectedClass.academic_year)
    },
    onSuccess: async () => {
      setMessage('Student assigned to the selected class.')
      setErrorMessage(null)
      await queryClient.invalidateQueries({ queryKey: ['students'] })
      await queryClient.invalidateQueries({ queryKey: ['students', student?.id] })
    },
    onError: (error) => setErrorMessage(toApiError(error).message),
  })
  const statusMutation = useMutation({
    mutationFn: () => {
      if (!student || !nextStatus) throw new Error('Select a supported status transition.')
      return schoolApi.students.updateStatus(student.id, nextStatus, reason)
    },
    onSuccess: async () => {
      setMessage('Student status updated.')
      setErrorMessage(null)
      await queryClient.invalidateQueries({ queryKey: ['students'] })
    },
    onError: (error) => setErrorMessage(toApiError(error).message),
  })
  const selectedClass = activeClassesQuery.data?.items.find((item) => item.id === Number(classId))
  const allowedNextStatuses = currentStudent ? statusTransitions[currentStudent.status] : []

  return (
    <FormDialog
      description="Enrollment updates use the active class and its academic year. Status changes only show transitions supported by the backend."
      onOpenChange={onOpenChange}
      open={open}
      title={student ? `Enrollment — ${student.first_name} ${student.last_name}` : 'Student enrollment'}
    >
      {message ? <SuccessState title="Student updated" description={message} /> : null}
      {errorMessage ? (
        <Alert className="mt-3" variant="destructive">
          <AlertTitle>Student update failed</AlertTitle>
          <AlertDescription>{errorMessage}</AlertDescription>
        </Alert>
      ) : null}
      <div className="grid gap-4">
        <section className="grid gap-3 rounded-lg border border-slate-200 p-4">
          <h3 className="text-sm font-semibold">Current enrollment</h3>
          <p className="text-sm text-slate-600">
            Current class ID: {currentStudent?.current_class_id ?? 'Not assigned'} · Status: {currentStudent?.status}
          </p>
          {!canReadClasses ? (
            <p className="text-sm text-slate-600">Class assignment requires the classes.read permission.</p>
          ) : activeClassesQuery.error ? (
            <ErrorState description={toApiError(activeClassesQuery.error).message} onRetry={() => void activeClassesQuery.refetch()} />
          ) : (
            <>
              <ClassRecordSelector
                classes={activeClassesQuery.data?.items ?? []}
                labelPrefix="Active class"
                onChange={(_, schoolClass) => setClassId(schoolClass ? String(schoolClass.id) : '')}
              />
              {selectedClass ? (
                <p className="text-xs text-slate-500">Academic year sent to the API: {selectedClass.academic_year}</p>
              ) : null}
              <Button
                disabled={!classId || assignClassMutation.isPending || !student?.id}
                onClick={() => {
                  setMessage(null)
                  setErrorMessage(null)
                  assignClassMutation.mutate()
                }}
                type="button"
              >
                {assignClassMutation.isPending ? 'Assigning…' : 'Assign to class'}
              </Button>
            </>
          )}
        </section>

        <section className="grid gap-3 rounded-lg border border-slate-200 p-4">
          <h3 className="text-sm font-semibold">Student status</h3>
          {allowedNextStatuses.length ? (
            <>
              <label className="grid gap-2 text-sm font-medium" htmlFor="student-next-status">
                Available transition from {currentStudent?.status}
                <select
                  className="h-10 rounded-lg border border-input bg-white px-3 font-normal"
                  id="student-next-status"
                  onChange={(event) => {
                    const selected = event.currentTarget.value
                    if (selected === '') {
                      setNextStatus('')
                      return
                    }
                    const matchingStatus = allowedNextStatuses.find((status) => status === selected)
                    if (matchingStatus) setNextStatus(matchingStatus)
                  }}
                  value={nextStatus}
                >
                  <option value="">Select status</option>
                  {allowedNextStatuses.map((status) => <option key={status} value={status}>{status}</option>)}
                </select>
              </label>
              <label className="grid gap-2 text-sm font-medium" htmlFor="student-status-reason">
                Reason (optional)
                <Input id="student-status-reason" onChange={(event) => setReason(event.target.value)} value={reason} />
              </label>
              <Button
                disabled={!nextStatus || statusMutation.isPending}
                onClick={() => {
                  setMessage(null)
                  setErrorMessage(null)
                  statusMutation.mutate()
                }}
                type="button"
                variant="outline"
              >
                {statusMutation.isPending ? 'Updating…' : 'Update status'}
              </Button>
            </>
          ) : <p className="text-sm text-slate-500">No status transitions are available from this state.</p>}
        </section>
      </div>
    </FormDialog>
  )
}

export function StudentsPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [classId, setClassId] = useState('')
  const [page, setPage] = useState(1)
  const [editingStudent, setEditingStudent] = useState<Student | null>(null)
  const [detailsStudent, setDetailsStudent] = useState<Student | null>(null)
  const [enrollmentStudent, setEnrollmentStudent] = useState<Student | null>(null)
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const canReadClasses = user?.permissions?.includes('classes.read') ?? false
  const query = useQuery({
    queryKey: ['students', { search, status, classId, page, limit: pageSize }],
    queryFn: () => schoolApi.students.list(
      { page, limit: pageSize, sort_by: 'first_name', sort_order: 'asc' },
      {
        search: search || undefined,
        status: status || undefined,
        current_class_id: classId ? Number(classId) : undefined,
      },
    ),
  })
  const classesQuery = useQuery({
    queryKey: ['classes', 'filter-options'],
    queryFn: () => schoolApi.classes.list(
      { page: 1, limit: 100, sort_by: 'name', sort_order: 'asc' },
      {},
    ),
    enabled: canReadClasses,
  })
  const deleteMutation = useMutation({
    mutationFn: (id: number) => schoolApi.students.delete(id),
    onSuccess: async () => {
      setSuccessMessage('Student record soft-deleted.')
      setErrorMessage(null)
      await queryClient.invalidateQueries({ queryKey: ['students'] })
    },
    onError: (error) => setErrorMessage(toApiError(error).message),
  })
  const canEdit = user?.permissions?.includes('students.update') ?? false
  const canDelete = user?.permissions?.includes('students.delete') ?? false
  const columns = useMemo(() => [
    { id: 'admission_no', header: 'Admission no.', cell: (student: Student) => student.admission_no ?? '—' },
    { id: 'name', header: 'Student', cell: (student: Student) => (
      <span className="font-medium">{student.first_name} {student.last_name}</span>
    ) },
    { id: 'class', header: 'Class ID', cell: (student: Student) => student.current_class_id ?? 'Unassigned' },
    { id: 'status', header: 'Status', cell: (student: Student) => <StatusBadge status={student.status} /> },
    { id: 'actions', header: 'Actions', cell: (student: Student) => (
      <div className="flex flex-wrap gap-2">
        <Button onClick={() => setDetailsStudent(student)} size="sm" variant="outline">View</Button>
        {canEdit ? (
          <>
            <Button onClick={() => {
              setEditingStudent(student)
              setErrorMessage(null)
            }} size="sm" variant="ghost">Edit</Button>
            <Button onClick={() => {
              setEnrollmentStudent(student)
              setErrorMessage(null)
            }} size="sm" variant="outline">Enrollment</Button>
          </>
        ) : null}
        {canDelete ? (
          <ConfirmDialog
            confirmLabel="Delete student"
            description="This soft-deletes the student record. Deleted students will no longer appear in normal API lists."
            onConfirm={async () => deleteMutation.mutateAsync(student.id)}
            title={`Delete ${student.first_name} ${student.last_name}?`}
            destructive
            trigger={<Button size="sm" variant="outline">Delete</Button>}
          />
        ) : null}
      </div>
    ) },
  ], [canDelete, canEdit, deleteMutation])

  return (
    <>
      <PageHeader
        actions={
          <PermissionGate anyOf={['students.create']}>
            <Button onClick={() => {
              setEditingStudent(null)
              setIsCreateOpen(true)
              setErrorMessage(null)
            }}>Add student</Button>
          </PermissionGate>
        }
        description="Search and manage student profiles, lifecycle status, and active class enrollment."
        title="Students"
      />
      {successMessage ? <SuccessState title="Student record updated" description={successMessage} /> : null}
      {errorMessage ? (
        <Alert className="mt-4" variant="destructive">
          <AlertTitle>Student operation failed</AlertTitle>
          <AlertDescription>{errorMessage}</AlertDescription>
        </Alert>
      ) : null}
      <div className="mt-5">
        <RecordList
          columns={columns}
          emptyMessage="No students match these filters."
          error={query.error ? toApiError(query.error).message : undefined}
          getRowId={(student) => student.id}
          isLoading={query.isLoading}
          onPageChange={setPage}
          onRetry={() => void query.refetch()}
          pagination={query.data?.pagination}
          rows={query.data?.items ?? []}
          toolbar={
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <SearchField
                label="Search students by name or admission number"
                onChange={(value) => {
                  setSearch(value)
                  setPage(1)
                }}
                placeholder="Search name or admission no."
                value={search}
              />
              <label className="sr-only" htmlFor="student-status-filter">Filter by status</label>
              <select
                className="h-10 rounded-lg border border-input bg-white px-3 text-sm"
                id="student-status-filter"
                onChange={(event) => {
                  setStatus(event.target.value)
                  setPage(1)
                }}
                value={status}
              >
                <option value="">All statuses</option>
                {Object.keys(statusTransitions).map((value) => <option key={value} value={value}>{value}</option>)}
              </select>
              {!canReadClasses ? (
                <p className="text-sm text-slate-600">Class filters require the classes.read permission.</p>
              ) : classesQuery.error ? (
                <span className="text-sm text-destructive">Class filters unavailable: {toApiError(classesQuery.error).message}</span>
              ) : (
                <ClassRecordSelector
                  classes={classesQuery.data?.items ?? []}
                  labelPrefix="Filter"
                  onChange={(_, schoolClass) => {
                    setClassId(schoolClass ? String(schoolClass.id) : '')
                    setPage(1)
                  }}
                />
              )}
            </div>
          }
        />
      </div>
      <StudentFormDialog
        key={`${editingStudent?.id ?? 'new'}-${isCreateOpen || editingStudent !== null}`}
        onOpenChange={(open) => {
          setIsCreateOpen(open)
          if (!open) setEditingStudent(null)
        }}
        open={isCreateOpen || editingStudent !== null}
        student={editingStudent}
      />
      <StudentDetailsDialog
        onOpenChange={(open) => {
          if (!open) setDetailsStudent(null)
        }}
        open={detailsStudent !== null}
        student={detailsStudent}
      />
      <StudentEnrollmentDialog
        key={`${enrollmentStudent?.id ?? 'no-student'}-${enrollmentStudent !== null}`}
        onOpenChange={(open) => {
          if (!open) setEnrollmentStudent(null)
        }}
        open={enrollmentStudent !== null}
        student={enrollmentStudent}
      />
    </>
  )
}
