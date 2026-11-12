import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { PermissionGate } from '@/components/auth/permission-gate'
import { FormDialog } from '@/components/school/form-dialog'
import { RecordList } from '@/components/school/record-list'
import { StatusBadge } from '@/components/school/status-badge'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { EmptyState, ErrorState, LoadingState, SuccessState } from '@/components/ui/async-state'
import { ConfirmDialog } from '@/components/ui/confirm-dialog'
import { FormField } from '@/components/ui/form-field'
import { Input } from '@/components/ui/input'
import { PageHeader } from '@/components/ui/page-header'
import { SearchableSelect } from '@/components/ui/searchable-select'
import { toApiError } from '@/lib/api/api-error'
import { useAuth } from '@/features/auth/auth-context'
import { schoolApi, type SchoolClass } from '@/features/school/school-api'

const classSchema = z.object({
  name: z.string().trim().min(1).max(100),
  section: z.string().trim().max(20),
  academic_year: z.string().trim().min(4).max(20),
  capacity: z.number().int().positive(),
  status: z.enum(['active', 'inactive']),
})

type ClassFormValues = z.infer<typeof classSchema>

function ClassFormDialog({
  schoolClass,
  open,
  onOpenChange,
}: {
  schoolClass: SchoolClass | null
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const queryClient = useQueryClient()
  const [formError, setFormError] = useState<string | null>(null)
  const catalogQuery = useQuery({
    queryKey: ['classes', 'catalog-inputs'],
    queryFn: () => schoolApi.classes.list(
      { page: 1, limit: 100, sort_by: 'name', sort_order: 'asc' },
      {},
    ),
    enabled: open,
  })
  const catalogClasses = catalogQuery.data?.items ?? []
  const gradeOptions = [...new Set(catalogClasses.map((item) => item.name))]
  const sectionOptions = [...new Set(catalogClasses
    .map((item) => item.section)
    .filter((section): section is string => Boolean(section)))]
  const yearOptions = [...new Set(catalogClasses.map((item) => item.academic_year))]
  const form = useForm<ClassFormValues>({
    resolver: zodResolver(classSchema),
    defaultValues: schoolClass
      ? {
          name: schoolClass.name,
          section: schoolClass.section ?? '',
          academic_year: schoolClass.academic_year,
          capacity: schoolClass.capacity,
          status: schoolClass.status,
        }
      : { name: '', section: '', academic_year: '', capacity: 30, status: 'active' },
  })
  const mutation = useMutation({
    mutationFn: (values: ClassFormValues) => schoolClass
      ? schoolApi.classes.update(schoolClass.id, {
          name: values.name,
          section: values.section || null,
          academic_year: values.academic_year,
          capacity: values.capacity,
          status: values.status,
        })
      : schoolApi.classes.create({
          name: values.name,
          section: values.section || null,
          academic_year: values.academic_year,
          capacity: values.capacity,
        }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['classes'] })
      onOpenChange(false)
    },
    onError: (error) => setFormError(toApiError(error).message),
  })

  return (
    <FormDialog
      description="Class activation, capacity, and uniqueness rules are validated by the API."
      onOpenChange={onOpenChange}
      open={open}
      title={schoolClass ? 'Edit class' : 'Add class'}
    >
      {formError ? (
        <Alert className="mb-3" variant="destructive">
          <AlertTitle>Class could not be saved</AlertTitle>
          <AlertDescription>{formError}</AlertDescription>
        </Alert>
      ) : null}
      {catalogQuery.error ? (
        <ErrorState description={`Class suggestions are unavailable: ${toApiError(catalogQuery.error).message}`} />
      ) : null}
      <form className="grid gap-4 sm:grid-cols-2" noValidate onSubmit={form.handleSubmit((values) => {
        setFormError(null)
        mutation.mutate(values)
      })}>
        <FormField error={form.formState.errors.name?.message} label="Class or grade" required>
          {({ id, describedBy }) => (
            <>
              <Input id={id} list={`${id}-options`} aria-describedby={describedBy} {...form.register('name')} />
              <datalist id={`${id}-options`}>
                {gradeOptions.map((grade) => <option key={grade} value={grade} />)}
              </datalist>
            </>
          )}
        </FormField>
        <FormField error={form.formState.errors.section?.message} label="Section">
          {({ id, describedBy }) => (
            <>
              <Input id={id} list={`${id}-options`} aria-describedby={describedBy} {...form.register('section')} />
              <datalist id={`${id}-options`}>
                {sectionOptions.map((section) => <option key={section} value={section} />)}
              </datalist>
            </>
          )}
        </FormField>
        <FormField error={form.formState.errors.academic_year?.message} label="Academic year" required>
          {({ id, describedBy }) => (
            <>
              <Input id={id} list={`${id}-options`} aria-describedby={describedBy} placeholder="2026-2027" {...form.register('academic_year')} />
              <datalist id={`${id}-options`}>
                {yearOptions.map((year) => <option key={year} value={year} />)}
              </datalist>
            </>
          )}
        </FormField>
        <FormField error={form.formState.errors.capacity?.message} label="Student capacity" required>
          {({ id, describedBy }) => (
            <Input
              id={id}
              type="number"
              min={1}
              aria-describedby={describedBy}
              {...form.register('capacity', { valueAsNumber: true })}
            />
          )}
        </FormField>
        {schoolClass ? (
          <FormField label="Status">
            {({ id }) => (
              <select id={id} className="h-10 rounded-lg border border-input bg-white px-3 text-sm" {...form.register('status')}>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            )}
          </FormField>
        ) : null}
        <div className="flex justify-end gap-2 sm:col-span-2">
          <Button onClick={() => onOpenChange(false)} type="button" variant="outline">Cancel</Button>
          <Button disabled={mutation.isPending} type="submit">{mutation.isPending ? 'Saving…' : 'Save class'}</Button>
        </div>
      </form>
    </FormDialog>
  )
}

function ClassManagementDialog({
  schoolClass,
  open,
  onOpenChange,
}: {
  schoolClass: SchoolClass | null
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [teacherId, setTeacherId] = useState('')
  const [subjectId, setSubjectId] = useState('')
  const [notice, setNotice] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)
  const id = schoolClass?.id
  const enabled = open && id !== undefined
  const canEdit = user?.permissions?.includes('classes.update') ?? false
  const readinessQuery = useQuery({
    queryKey: ['classes', id, 'readiness'],
    queryFn: () => schoolApi.classes.readiness(id!),
    enabled,
  })
  const subjectsQuery = useQuery({
    queryKey: ['classes', id, 'subjects'],
    queryFn: () => schoolApi.classes.subjects(id!),
    enabled,
  })
  const teachersQuery = useQuery({
    queryKey: ['teachers', 'active-options'],
    queryFn: () => schoolApi.teachers.list(
      { page: 1, limit: 100, sort_by: 'first_name', sort_order: 'asc' },
      { status: 'active' },
    ),
    enabled,
  })
  const subjectsCatalogQuery = useQuery({
    queryKey: ['subjects', 'active-options'],
    queryFn: () => schoolApi.subjects.list(
      { page: 1, limit: 100, sort_by: 'name', sort_order: 'asc' },
      { active: true },
    ),
    enabled,
  })
  const relationMutation = useMutation({
    mutationFn: async (action: 'assign-teacher' | 'assign-subject') => {
      if (action === 'assign-teacher') {
        return schoolApi.classes.assignTeacher(id!, Number(teacherId), Boolean(schoolClass?.class_teacher_id))
      }
      return schoolApi.classes.assignSubject(id!, Number(subjectId))
    },
    onSuccess: async (_result, action) => {
      setNotice(action === 'assign-teacher' ? 'Class teacher saved.' : 'Subject offering saved.')
      setActionError(null)
      setTeacherId('')
      setSubjectId('')
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['classes'] }),
        queryClient.invalidateQueries({ queryKey: ['classes', id, 'readiness'] }),
        queryClient.invalidateQueries({ queryKey: ['classes', id, 'subjects'] }),
      ])
    },
    onError: (error) => setActionError(toApiError(error).message),
  })
  const removeSubjectMutation = useMutation({
    mutationFn: (targetSubjectId: number) => schoolApi.classes.removeSubject(id!, targetSubjectId),
    onSuccess: async () => {
      setNotice('Subject offering removed.')
      setActionError(null)
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['classes', id, 'subjects'] }),
        queryClient.invalidateQueries({ queryKey: ['classes', id, 'readiness'] }),
      ])
    },
    onError: (error) => setActionError(toApiError(error).message),
  })
  const removeTeacherMutation = useMutation({
    mutationFn: () => schoolApi.classes.removeTeacher(id!),
    onSuccess: async () => {
      setNotice('Class teacher removed.')
      await queryClient.invalidateQueries({ queryKey: ['classes'] })
      await queryClient.invalidateQueries({ queryKey: ['classes', id, 'readiness'] })
    },
    onError: (error) => setActionError(toApiError(error).message),
  })
  const assignedSubjectIds = new Set((subjectsQuery.data ?? []).map((subject) => subject.id))

  return (
    <FormDialog
      description="The designated class teacher is a separate relationship from subject teaching assignments."
      onOpenChange={onOpenChange}
      open={open}
      title={schoolClass ? `Class setup — ${schoolClass.name}${schoolClass.section ? ` · ${schoolClass.section}` : ''}` : 'Class setup'}
    >
      {notice ? <SuccessState title="Class setup updated" description={notice} /> : null}
      {actionError ? (
        <Alert className="mt-3" variant="destructive">
          <AlertTitle>Class setup action failed</AlertTitle>
          <AlertDescription>{actionError}</AlertDescription>
        </Alert>
      ) : null}
      <section className="grid gap-3 rounded-lg border border-slate-200 p-4">
        <h3 className="text-sm font-semibold">Academic readiness</h3>
        {readinessQuery.isLoading ? <LoadingState label="Checking readiness" /> : null}
        {readinessQuery.error ? (
          <ErrorState description={toApiError(readinessQuery.error).message} onRetry={() => void readinessQuery.refetch()} />
        ) : null}
        {readinessQuery.data ? (
          <>
            <StatusBadge status={readinessQuery.data.ready ? 'ready' : 'not_ready'} />
            {readinessQuery.data.issues.length ? (
              <ul className="list-disc space-y-1 pl-5 text-sm text-amber-800">
                {readinessQuery.data.issues.map((issue) => <li key={issue}>{issue}</li>)}
              </ul>
            ) : <p className="text-sm text-slate-600">The class meets the configured readiness checks.</p>}
          </>
        ) : null}
      </section>

      <section className="grid gap-3 rounded-lg border border-slate-200 p-4">
        <h3 className="text-sm font-semibold">Designated class teacher</h3>
        <p className="text-xs text-slate-500">A teacher may be designated class teacher for only one class.</p>
        {teachersQuery.error ? (
          <ErrorState description={toApiError(teachersQuery.error).message} onRetry={() => void teachersQuery.refetch()} />
        ) : (
          <SearchableSelect
            label="Active teacher"
            onChange={setTeacherId}
            options={(teachersQuery.data?.items ?? []).map((teacher) => ({
              value: String(teacher.id),
              label: `${teacher.first_name} ${teacher.last_name} · ${teacher.employee_no}`,
            }))}
            value={teacherId}
          />
        )}
        {canEdit ? (
          <div className="flex flex-wrap gap-2">
            <Button
              disabled={!teacherId || relationMutation.isPending}
              onClick={() => {
                setActionError(null)
                relationMutation.mutate('assign-teacher')
              }}
            >
              {schoolClass?.class_teacher_id ? 'Replace class teacher' : 'Assign class teacher'}
            </Button>
            {schoolClass?.class_teacher_id ? (
              <ConfirmDialog
                confirmLabel="Remove class teacher"
                description="This removes the class’s designated teacher assignment."
                onConfirm={async () => removeTeacherMutation.mutateAsync()}
                title="Remove class teacher?"
                destructive
                trigger={<Button variant="outline">Remove assignment</Button>}
              />
            ) : null}
          </div>
        ) : null}
      </section>

      <section className="grid gap-3 rounded-lg border border-slate-200 p-4">
        <h3 className="text-sm font-semibold">Subject offerings for this class</h3>
        {subjectsQuery.isLoading ? <LoadingState label="Loading class subject offerings" /> : null}
        {subjectsQuery.error ? (
          <ErrorState description={toApiError(subjectsQuery.error).message} onRetry={() => void subjectsQuery.refetch()} />
        ) : subjectsQuery.data?.length ? (
          <ul className="divide-y divide-slate-200 rounded-lg border border-slate-200">
            {subjectsQuery.data.map((subject) => (
              <li className="flex items-center justify-between gap-3 p-3" key={subject.id}>
                <span className="text-sm"><strong>{subject.code}</strong> · {subject.name}</span>
                {canEdit ? (
                  <ConfirmDialog
                    confirmLabel="Remove offering"
                    description="The API prevents removal while active students are enrolled in this class."
                    onConfirm={async () => removeSubjectMutation.mutateAsync(subject.id)}
                    title="Remove subject offering?"
                    destructive
                    trigger={<Button size="sm" variant="outline">Remove</Button>}
                  />
                ) : null}
              </li>
            ))}
          </ul>
        ) : subjectsQuery.data ? (
          <EmptyState title="No subject offerings" description="Add active catalog subjects to make them available for this class." />
        ) : null}
        {canEdit ? (
          <>
            {subjectsCatalogQuery.error ? (
              <ErrorState description={toApiError(subjectsCatalogQuery.error).message} onRetry={() => void subjectsCatalogQuery.refetch()} />
            ) : (
              <SearchableSelect
                label="Active catalog subject"
                onChange={setSubjectId}
                options={(subjectsCatalogQuery.data?.items ?? [])
                  .filter((subject) => !assignedSubjectIds.has(subject.id))
                  .map((subject) => ({ value: String(subject.id), label: `${subject.code} · ${subject.name}` }))}
                value={subjectId}
              />
            )}
            <Button
              disabled={!subjectId || relationMutation.isPending}
              onClick={() => {
                setActionError(null)
                relationMutation.mutate('assign-subject')
              }}
              type="button"
              variant="outline"
            >
              Add subject offering
            </Button>
          </>
        ) : null}
      </section>
    </FormDialog>
  )
}

export function ClassesPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [grade, setGrade] = useState('')
  const [section, setSection] = useState('')
  const [academicYear, setAcademicYear] = useState('')
  const [status, setStatus] = useState('')
  const [page, setPage] = useState(1)
  const [editingClass, setEditingClass] = useState<SchoolClass | null>(null)
  const [managingClass, setManagingClass] = useState<SchoolClass | null>(null)
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const catalogQuery = useQuery({
    queryKey: ['classes', 'filter-options'],
    queryFn: () => schoolApi.classes.list(
      { page: 1, limit: 100, sort_by: 'name', sort_order: 'asc' },
      {},
    ),
  })
  const catalogClasses = catalogQuery.data?.items ?? []
  const gradeOptions = [...new Set(catalogClasses.map((item) => item.name))]
  const sectionOptions = [...new Set(catalogClasses.map((item) => item.section ?? '__no_section__'))]
  const yearOptions = [...new Set(catalogClasses.map((item) => item.academic_year))].sort().reverse()
  const query = useQuery({
    queryKey: ['classes', { grade, section, academicYear, status, page, limit: 10 }],
    queryFn: () => schoolApi.classes.list(
      { page, limit: 10, sort_by: 'name', sort_order: 'asc' },
      {
        name: grade || undefined,
        section: section && section !== '__no_section__' ? section : undefined,
        section_is_null: section === '__no_section__' ? true : undefined,
        academic_year: academicYear || undefined,
        status: status || undefined,
      },
    ),
  })
  const deleteMutation = useMutation({
    mutationFn: (id: number) => schoolApi.classes.delete(id),
    onSuccess: async () => {
      setSuccessMessage('Class deleted.')
      setErrorMessage(null)
      await queryClient.invalidateQueries({ queryKey: ['classes'] })
    },
    onError: (error) => setErrorMessage(toApiError(error).message),
  })
  const canEdit = user?.permissions?.includes('classes.update') ?? false
  const canDelete = user?.permissions?.includes('classes.delete') ?? false
  const columns = [
    { id: 'name', header: 'Class', cell: (item: SchoolClass) => (
      <span className="font-medium">{item.name}{item.section ? ` · ${item.section}` : ''}</span>
    ) },
    { id: 'year', header: 'Academic year', cell: (item: SchoolClass) => item.academic_year },
    { id: 'capacity', header: 'Capacity', cell: (item: SchoolClass) => item.capacity },
    { id: 'class_teacher', header: 'Class teacher ID', cell: (item: SchoolClass) => item.class_teacher_id ?? 'Not assigned' },
    { id: 'status', header: 'Status', cell: (item: SchoolClass) => <StatusBadge status={item.status} /> },
    { id: 'actions', header: 'Actions', cell: (item: SchoolClass) => (
      <div className="flex flex-wrap gap-2">
        <Button onClick={() => {
          setManagingClass(item)
          setErrorMessage(null)
        }} size="sm" variant="outline">Manage setup</Button>
        {canEdit ? (
          <Button onClick={() => {
            setEditingClass(item)
            setErrorMessage(null)
          }} size="sm" variant="ghost">Edit</Button>
        ) : null}
        {canDelete ? (
          <ConfirmDialog
            confirmLabel="Delete class"
            description="Classes with active students cannot be deleted. This operation is permanent in the API."
            onConfirm={async () => deleteMutation.mutateAsync(item.id)}
            title={`Delete ${item.name}?`}
            destructive
            trigger={<Button size="sm" variant="outline">Delete</Button>}
          />
        ) : null}
      </div>
    ) },
  ]

  return (
    <>
      <PageHeader
        actions={
          <PermissionGate anyOf={['classes.create']}>
            <Button onClick={() => {
              setEditingClass(null)
              setIsCreateOpen(true)
              setErrorMessage(null)
            }}>Add class</Button>
          </PermissionGate>
        }
        description="Configure class sections, annual capacity, a single class teacher, and available subject offerings."
        title="Classes"
      />
      {successMessage ? <SuccessState title="Class operation completed" description={successMessage} /> : null}
      {errorMessage ? (
        <Alert className="mt-4" variant="destructive">
          <AlertTitle>Class operation failed</AlertTitle>
          <AlertDescription>{errorMessage}</AlertDescription>
        </Alert>
      ) : null}
      <div className="mt-5">
        <RecordList
          columns={columns}
          emptyMessage="No classes match these filters."
          error={query.error ? toApiError(query.error).message : undefined}
          getRowId={(item) => item.id}
          isLoading={query.isLoading}
          onPageChange={setPage}
          onRetry={() => void query.refetch()}
          pagination={query.data?.pagination}
          rows={query.data?.items ?? []}
          toolbar={
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              <label className="grid gap-2 text-sm font-medium" htmlFor="class-grade">
                Grade
                <select
                  className="h-10 rounded-lg border border-input bg-white px-3 text-sm"
                  id="class-grade"
                  onChange={(event) => {
                    setGrade(event.target.value)
                    setPage(1)
                  }}
                  value={grade}
                >
                  <option value="">All grades</option>
                  {gradeOptions.map((item) => <option key={item} value={item}>{item}</option>)}
                </select>
              </label>
              <label className="grid gap-2 text-sm font-medium" htmlFor="class-section">
                Section
                <select
                  className="h-10 rounded-lg border border-input bg-white px-3 text-sm"
                  id="class-section"
                  onChange={(event) => {
                    setSection(event.target.value)
                    setPage(1)
                  }}
                  value={section}
                >
                  <option value="">All sections</option>
                  {sectionOptions.map((item) => (
                    <option key={item} value={item}>
                      {item === '__no_section__' ? 'No section' : item}
                    </option>
                  ))}
                </select>
              </label>
              <label className="grid gap-2 text-sm font-medium" htmlFor="class-year">
                Academic year
                <select
                  className="h-10 rounded-lg border border-input bg-white px-3 text-sm"
                  id="class-year"
                  onChange={(event) => {
                    setAcademicYear(event.target.value)
                    setPage(1)
                  }}
                  value={academicYear}
                >
                  <option value="">All academic years</option>
                  {yearOptions.map((item) => <option key={item} value={item}>{item}</option>)}
                </select>
              </label>
              <label className="grid gap-2 text-sm font-medium" htmlFor="class-status">
                Status
                <select
                  className="h-10 rounded-lg border border-input bg-white px-3 text-sm"
                  id="class-status"
                  onChange={(event) => {
                    setStatus(event.target.value)
                    setPage(1)
                  }}
                  value={status}
                >
                  <option value="">All statuses</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                </select>
              </label>
            </div>
          }
        />
      </div>
      <ClassFormDialog
        key={`${editingClass?.id ?? 'new'}-${isCreateOpen || editingClass !== null}`}
        onOpenChange={(open) => {
          setIsCreateOpen(open)
          if (!open) setEditingClass(null)
        }}
        open={isCreateOpen || editingClass !== null}
        schoolClass={editingClass}
      />
      <ClassManagementDialog
        key={`${managingClass?.id ?? 'no-class'}-${managingClass !== null}`}
        onOpenChange={(open) => {
          if (!open) setManagingClass(null)
        }}
        open={managingClass !== null}
        schoolClass={managingClass}
      />
    </>
  )
}
