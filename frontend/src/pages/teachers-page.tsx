import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { PermissionGate } from '@/components/auth/permission-gate'
import { ClassRecordSelector } from '@/components/school/class-record-selector'
import { RecordList } from '@/components/school/record-list'
import { FormDialog } from '@/components/school/form-dialog'
import { StatusBadge } from '@/components/school/status-badge'
import { ConfirmDialog } from '@/components/ui/confirm-dialog'
import { FormField } from '@/components/ui/form-field'
import { Input } from '@/components/ui/input'
import { PageHeader } from '@/components/ui/page-header'
import { SearchField } from '@/components/ui/search-field'
import { SearchableSelect } from '@/components/ui/searchable-select'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { EmptyState, ErrorState, LoadingState, SuccessState } from '@/components/ui/async-state'
import { toApiError } from '@/lib/api/api-error'
import type { ApiPagination } from '@/lib/api/types'
import { useAuth } from '@/features/auth/auth-context'
import { schoolApi, type Teacher, type TeacherCreate } from '@/features/school/school-api'

const pageSize = 10
const teacherSchema = z.object({
  employee_no: z.string().trim().min(1).max(50),
  first_name: z.string().trim().min(1).max(100),
  last_name: z.string().trim().min(1).max(100),
  email: z.string().email(),
  phone: z.string().trim().min(5).max(30),
  joining_date: z.string().min(1),
  status: z.enum(['active', 'inactive', 'resigned']),
})

type TeacherFormValues = z.infer<typeof teacherSchema>
const defaultValues: TeacherFormValues = {
  employee_no: '',
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  joining_date: '',
  status: 'active',
}

function useTeacherList(search: string, status: string, page: number) {
  return useQuery({
    queryKey: ['teachers', { search, status, page, limit: pageSize }],
    queryFn: () =>
      schoolApi.teachers.list(
        { page, limit: pageSize, sort_by: 'first_name', sort_order: 'asc' },
        { search: search || undefined, status: status || undefined },
      ),
  })
}

function TeacherFormDialog({
  teacher,
  open,
  onOpenChange,
}: {
  teacher: Teacher | null
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const queryClient = useQueryClient()
  const [formError, setFormError] = useState<string | null>(null)
  const isEditing = teacher !== null
  const form = useForm<TeacherFormValues>({
    resolver: zodResolver(teacherSchema),
    defaultValues: teacher
      ? {
          employee_no: teacher.employee_no,
          first_name: teacher.first_name,
          last_name: teacher.last_name,
          email: teacher.email,
          phone: teacher.phone ?? '',
          joining_date: teacher.joining_date ?? '',
          status: teacher.status,
        }
      : defaultValues,
  })

  const mutation = useMutation({
    mutationFn: (values: TeacherFormValues) => {
      if (teacher) {
        return schoolApi.teachers.update(teacher.id, {
          first_name: values.first_name,
          last_name: values.last_name,
          email: values.email,
          phone: values.phone,
          status: values.status,
        })
      }

      const payload: TeacherCreate = {
        employee_no: values.employee_no,
        first_name: values.first_name,
        last_name: values.last_name,
        email: values.email,
        phone: values.phone,
        joining_date: values.joining_date,
      }
      return schoolApi.teachers.create(payload)
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['teachers'] })
      onOpenChange(false)
    },
    onError: (error) => setFormError(toApiError(error).message),
  })

  return (
    <FormDialog
      description={isEditing
        ? 'Update the teacher profile and employment status.'
        : 'Create a teacher record using the fields required by the API.'}
      onOpenChange={onOpenChange}
      open={open}
      title={isEditing ? 'Edit teacher' : 'Add teacher'}
    >
      {formError ? (
        <Alert className="mb-4" variant="destructive">
          <AlertTitle>Teacher could not be saved</AlertTitle>
          <AlertDescription>{formError}</AlertDescription>
        </Alert>
      ) : null}
      <form className="grid gap-4 sm:grid-cols-2" noValidate onSubmit={form.handleSubmit((values) => {
        setFormError(null)
        mutation.mutate(values)
      })}>
        {!isEditing ? (
          <FormField error={form.formState.errors.employee_no?.message} label="Employee number" required>
            {({ id, describedBy }) => (
              <Input id={id} aria-describedby={describedBy} {...form.register('employee_no')} />
            )}
          </FormField>
        ) : null}
        <FormField error={form.formState.errors.first_name?.message} label="First name" required>
          {({ id, describedBy }) => (
            <Input id={id} aria-describedby={describedBy} {...form.register('first_name')} />
          )}
        </FormField>
        <FormField error={form.formState.errors.last_name?.message} label="Last name" required>
          {({ id, describedBy }) => (
            <Input id={id} aria-describedby={describedBy} {...form.register('last_name')} />
          )}
        </FormField>
        <FormField error={form.formState.errors.email?.message} label="Work email" required>
          {({ id, describedBy }) => (
            <Input id={id} type="email" aria-describedby={describedBy} {...form.register('email')} />
          )}
        </FormField>
        <FormField error={form.formState.errors.phone?.message} label="Phone" required>
          {({ id, describedBy }) => (
            <Input id={id} type="tel" aria-describedby={describedBy} {...form.register('phone')} />
          )}
        </FormField>
        {!isEditing ? (
          <FormField error={form.formState.errors.joining_date?.message} label="Joining date" required>
            {({ id, describedBy }) => (
              <Input id={id} type="date" aria-describedby={describedBy} {...form.register('joining_date')} />
            )}
          </FormField>
        ) : (
          <FormField error={form.formState.errors.status?.message} label="Employment status" required>
            {({ id, describedBy }) => (
              <select
                id={id}
                aria-describedby={describedBy}
                className="h-10 rounded-lg border border-input bg-white px-3 text-sm"
                {...form.register('status')}
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="resigned">Resigned</option>
              </select>
            )}
          </FormField>
        )}
        <div className="flex justify-end gap-2 sm:col-span-2">
          <Button onClick={() => onOpenChange(false)} type="button" variant="outline">Cancel</Button>
          <Button disabled={mutation.isPending} type="submit">
            {mutation.isPending ? 'Saving…' : isEditing ? 'Save changes' : 'Create teacher'}
          </Button>
        </div>
      </form>
    </FormDialog>
  )
}

function TeacherAssignmentsDialog({
  teacher,
  open,
  onOpenChange,
}: {
  teacher: Teacher | null
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [classId, setClassId] = useState('')
  const [subjectId, setSubjectId] = useState('')
  const [message, setMessage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const canEdit = user?.permissions?.includes('teachers.update') ?? false
  const canAssign = canEdit
    && (user?.permissions?.includes('classes.read') ?? false)
    && (user?.permissions?.includes('subjects.read') ?? false)
  const enabled = open && teacher !== null
  const assignmentsQuery = useQuery({
    queryKey: ['teachers', teacher?.id, 'class-subjects'],
    queryFn: () => schoolApi.teachers.classSubjects(teacher!.id),
    enabled,
  })
  const classesQuery = useQuery({
    queryKey: ['classes', 'active-options'],
    queryFn: () => schoolApi.classes.list(
      { page: 1, limit: 100, sort_by: 'name', sort_order: 'asc' },
      { status: 'active' },
    ),
    enabled: enabled && canAssign,
  })
  const offeringsQuery = useQuery({
    queryKey: ['classes', classId, 'subjects'],
    queryFn: () => schoolApi.classes.subjects(Number(classId)),
    enabled: enabled && canAssign && Boolean(classId),
  })
  const assignmentMutation = useMutation({
    mutationFn: () => schoolApi.teachers.assignClassSubject(
      teacher!.id,
      Number(classId),
      Number(subjectId),
    ),
    onSuccess: async () => {
      setMessage('Teacher assignment saved.')
      setErrorMessage(null)
      setSubjectId('')
      await queryClient.invalidateQueries({ queryKey: ['teachers', teacher?.id, 'class-subjects'] })
    },
    onError: (error) => setErrorMessage(toApiError(error).message),
  })
  const removalMutation = useMutation({
    mutationFn: (assignment: { class_id: number; subject_id: number }) =>
      schoolApi.teachers.removeClassSubject(teacher!.id, assignment.class_id, assignment.subject_id),
    onSuccess: async () => {
      setMessage('Teacher assignment removed.')
      await queryClient.invalidateQueries({ queryKey: ['teachers', teacher?.id, 'class-subjects'] })
    },
    onError: (error) => setErrorMessage(toApiError(error).message),
  })

  return (
    <FormDialog
      description="These are class-specific subject teaching allocations. They are separate from the single designated class teacher."
      onOpenChange={onOpenChange}
      open={open}
      title={teacher ? `Teaching assignments — ${teacher.first_name} ${teacher.last_name}` : 'Teaching assignments'}
    >
      {message ? <SuccessState title="Assignment updated" description={message} /> : null}
      {errorMessage ? (
        <Alert className="mt-3" variant="destructive">
          <AlertTitle>Assignment failed</AlertTitle>
          <AlertDescription>{errorMessage}</AlertDescription>
        </Alert>
      ) : null}
      {assignmentsQuery.isLoading ? <LoadingState label="Loading teaching assignments" /> : null}
      {assignmentsQuery.error ? (
        <ErrorState description={toApiError(assignmentsQuery.error).message} onRetry={() => void assignmentsQuery.refetch()} />
      ) : null}
      {assignmentsQuery.data ? (
        assignmentsQuery.data.length ? (
          <ul className="divide-y divide-slate-200 rounded-lg border border-slate-200">
            {assignmentsQuery.data.map((assignment) => (
              <li className="flex items-center justify-between gap-3 p-3" key={`${assignment.class_id}-${assignment.subject_id}`}>
                <span className="text-sm">
                  <strong>{assignment.subject_name}</strong>
                  <span className="block text-xs text-slate-500">{assignment.class_name}</span>
                </span>
                {canEdit ? <ConfirmDialog
                  confirmLabel="Remove assignment"
                  description="Remove this teacher’s class-specific subject allocation?"
                  onConfirm={async () => removalMutation.mutateAsync(assignment)}
                  title="Remove teaching assignment"
                  destructive
                  trigger={<Button size="sm" variant="outline">Remove</Button>}
                /> : null}
              </li>
            ))}
          </ul>
        ) : <EmptyState title="No teaching assignments" description="No class-specific subject allocations are assigned to this teacher." />
      ) : null}
      {canAssign ? <form className="grid gap-3 rounded-lg border border-slate-200 p-4" onSubmit={(event) => {
        event.preventDefault()
        setMessage(null)
        setErrorMessage(null)
        assignmentMutation.mutate()
      }}>
        <p className="text-sm font-medium">Assign a subject in a class</p>
        {classesQuery.error ? (
          <ErrorState description={toApiError(classesQuery.error).message} onRetry={() => void classesQuery.refetch()} />
        ) : (
          <ClassRecordSelector
            classes={classesQuery.data?.items ?? []}
            labelPrefix="Active class"
            onChange={(_, schoolClass) => {
              setClassId(schoolClass ? String(schoolClass.id) : '')
              setSubjectId('')
            }}
          />
        )}
        {offeringsQuery.error ? (
          <ErrorState description={toApiError(offeringsQuery.error).message} onRetry={() => void offeringsQuery.refetch()} />
        ) : (
          <SearchableSelect
            label="Subject offered in selected class"
            onChange={setSubjectId}
            options={(offeringsQuery.data ?? []).filter((item) => item.is_active).map((item) => ({
              value: String(item.id),
              label: `${item.code} · ${item.name}`,
            }))}
            value={subjectId}
            disabled={!classId || offeringsQuery.isLoading}
          />
        )}
        <Button
          disabled={!classId || !subjectId || assignmentMutation.isPending || !offeringsQuery.data?.length}
          type="submit"
        >
          {assignmentMutation.isPending ? 'Assigning…' : 'Assign subject'}
        </Button>
        {offeringsQuery.data?.length === 0 ? (
          <p className="text-xs text-amber-700">This class has no active subject offerings. Add an offering from Class Management first.</p>
        ) : null}
      </form> : null}
    </FormDialog>
  )
}

export function TeachersPage() {
  const { user } = useAuth()
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [page, setPage] = useState(1)
  const [editingTeacher, setEditingTeacher] = useState<Teacher | null>(null)
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [assigningTeacher, setAssigningTeacher] = useState<Teacher | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const query = useTeacherList(search, status, page)
  const canEdit = user?.permissions?.includes('teachers.update') ?? false
  const pagination: ApiPagination | undefined = query.data?.pagination
  const columns = [
    { id: 'employee_no', header: 'Employee no.', cell: (teacher: Teacher) => teacher.employee_no },
    { id: 'name', header: 'Teacher', cell: (teacher: Teacher) => (
      <span className="font-medium">{teacher.first_name} {teacher.last_name}</span>
    ) },
    { id: 'email', header: 'Work email', cell: (teacher: Teacher) => teacher.email },
    { id: 'status', header: 'Status', cell: (teacher: Teacher) => <StatusBadge status={teacher.status} /> },
    { id: 'actions', header: 'Actions', cell: (teacher: Teacher) => (
      <div className="flex flex-wrap gap-2">
        <Button
          onClick={() => {
            setSuccessMessage(null)
            setAssigningTeacher(teacher)
          }}
          size="sm"
          variant="outline"
        >
          Teaching assignments
        </Button>
        {canEdit ? (
          <Button
            onClick={() => {
              setSuccessMessage(null)
              setEditingTeacher(teacher)
            }}
            size="sm"
            variant="ghost"
          >
            Edit
          </Button>
        ) : null}
      </div>
    ) },
  ]

  return (
    <>
      <PageHeader
        actions={
          <PermissionGate anyOf={['teachers.create']}>
            <Button onClick={() => {
              setSuccessMessage(null)
              setEditingTeacher(null)
              setIsCreateOpen(true)
            }}>Add teacher</Button>
          </PermissionGate>
        }
        description="Manage teacher profiles, employment status, and class-specific subject teaching allocations."
        title="Teachers"
      />
      {successMessage ? <SuccessState title="Teacher updated" description={successMessage} /> : null}
      <div className="mt-5">
        <RecordList
          columns={columns}
          emptyMessage="No teachers match these filters."
          error={query.error ? toApiError(query.error).message : undefined}
          getRowId={(teacher) => teacher.id}
          isLoading={query.isLoading}
          onPageChange={setPage}
          onRetry={() => void query.refetch()}
          pagination={pagination}
          rows={query.data?.items ?? []}
          toolbar={
            <div className="flex flex-col gap-3 sm:flex-row">
              <SearchField
                label="Search teachers by name or employee number"
                onChange={(value) => {
                  setSearch(value)
                  setPage(1)
                }}
                placeholder="Search name or employee no."
                value={search}
              />
              <label className="sr-only" htmlFor="teacher-status">Filter by status</label>
              <select
                className="h-10 rounded-lg border border-input bg-white px-3 text-sm"
                id="teacher-status"
                onChange={(event) => {
                  setStatus(event.target.value)
                  setPage(1)
                }}
                value={status}
              >
                <option value="">All statuses</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="resigned">Resigned</option>
              </select>
            </div>
          }
        />
      </div>
      <TeacherFormDialog
        key={`${editingTeacher?.id ?? 'new'}-${isCreateOpen || editingTeacher !== null}`}
        onOpenChange={(open) => {
          setIsCreateOpen(open)
          if (!open) setEditingTeacher(null)
        }}
        open={isCreateOpen || editingTeacher !== null}
        teacher={editingTeacher}
      />
      <TeacherAssignmentsDialog
        key={`${assigningTeacher?.id ?? 'no-teacher'}-${assigningTeacher !== null}`}
        onOpenChange={(open) => {
          if (!open) setAssigningTeacher(null)
        }}
        open={assigningTeacher !== null}
        teacher={assigningTeacher}
      />
    </>
  )
}
