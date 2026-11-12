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
import { SuccessState } from '@/components/ui/async-state'
import { ConfirmDialog } from '@/components/ui/confirm-dialog'
import { FormField } from '@/components/ui/form-field'
import { Input } from '@/components/ui/input'
import { PageHeader } from '@/components/ui/page-header'
import { SearchField } from '@/components/ui/search-field'
import { toApiError } from '@/lib/api/api-error'
import { useAuth } from '@/features/auth/auth-context'
import { schoolApi, type Subject } from '@/features/school/school-api'

const subjectSchema = z.object({
  code: z.string().trim().min(1).max(50),
  name: z.string().trim().min(1).max(100),
  category: z.string().trim().max(100),
  description: z.string().trim().max(2000),
  subject_type: z.enum(['mandatory', 'elective', 'optional']),
  max_marks: z.string(),
  passing_marks: z.string(),
}).superRefine((value, context) => {
  const maximum = value.max_marks.trim() ? Number(value.max_marks) : null
  const passing = value.passing_marks.trim() ? Number(value.passing_marks) : null
  if ((maximum === null) !== (passing === null)) {
    context.addIssue({
      code: 'custom',
      path: ['passing_marks'],
      message: 'Enter both maximum and passing marks, or leave both blank.',
    })
  } else if (maximum !== null && (!Number.isFinite(maximum) || maximum <= 0 || passing! < 0 || passing! > maximum)) {
    context.addIssue({
      code: 'custom',
      path: ['passing_marks'],
      message: 'Passing marks must be between zero and maximum marks.',
    })
  }
})

type SubjectFormValues = z.infer<typeof subjectSchema>

function SubjectFormDialog({
  subject,
  open,
  onOpenChange,
}: {
  subject: Subject | null
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const queryClient = useQueryClient()
  const [formError, setFormError] = useState<string | null>(null)
  const form = useForm<SubjectFormValues>({
    resolver: zodResolver(subjectSchema),
    defaultValues: subject
      ? {
          code: subject.code,
          name: subject.name,
          category: subject.category ?? '',
          description: subject.description ?? '',
          subject_type: subject.subject_type,
          max_marks: subject.max_marks === null ? '' : String(subject.max_marks),
          passing_marks: subject.passing_marks === null ? '' : String(subject.passing_marks),
        }
      : {
          code: '',
          name: '',
          category: '',
          description: '',
          subject_type: 'mandatory',
          max_marks: '',
          passing_marks: '',
        },
  })
  const mutation = useMutation({
    mutationFn: (values: SubjectFormValues) => {
      const payload = {
        ...values,
        code: values.code.toUpperCase(),
        category: values.category || null,
        description: values.description || null,
        max_marks: values.max_marks.trim() ? Number(values.max_marks) : null,
        passing_marks: values.passing_marks.trim() ? Number(values.passing_marks) : null,
      }
      return subject
        ? schoolApi.subjects.update(subject.id, payload)
        : schoolApi.subjects.create(payload)
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['subjects'] })
      await queryClient.invalidateQueries({ queryKey: ['classes'] })
      onOpenChange(false)
    },
    onError: (error) => setFormError(toApiError(error).message),
  })

  return (
    <FormDialog
      description="Subject codes are normalized to uppercase. Duplicate codes are rejected by the API."
      onOpenChange={onOpenChange}
      open={open}
      title={subject ? 'Edit subject' : 'Add subject'}
    >
      {formError ? (
        <Alert className="mb-3" variant="destructive">
          <AlertTitle>Subject could not be saved</AlertTitle>
          <AlertDescription>{formError}</AlertDescription>
        </Alert>
      ) : null}
      <form className="grid gap-4" noValidate onSubmit={form.handleSubmit((values) => {
        setFormError(null)
        mutation.mutate(values)
      })}>
        <FormField error={form.formState.errors.code?.message} label="Subject code" required>
          {({ id, describedBy }) => (
            <Input id={id} aria-describedby={describedBy} autoCapitalize="characters" {...form.register('code')} />
          )}
        </FormField>
        <FormField error={form.formState.errors.name?.message} label="Subject name" required>
          {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('name')} />}
        </FormField>
        <FormField error={form.formState.errors.category?.message} label="Category">
          {({ id, describedBy }) => <Input id={id} aria-describedby={describedBy} {...form.register('category')} />}
        </FormField>
        <FormField error={form.formState.errors.subject_type?.message} label="Catalog classification" required>
          {({ id, describedBy }) => (
            <select
              className="h-10 rounded-lg border border-input bg-white px-3 text-sm"
              id={id}
              aria-describedby={describedBy}
              {...form.register('subject_type')}
            >
              <option value="mandatory">Mandatory</option>
              <option value="elective">Elective</option>
              <option value="optional">Optional</option>
            </select>
          )}
        </FormField>
        <div className="grid gap-4 sm:grid-cols-2">
          <FormField error={form.formState.errors.max_marks?.message} label="Default maximum marks">
            {({ id, describedBy }) => (
              <Input id={id} aria-describedby={describedBy} min="0.01" step="0.01" type="number" {...form.register('max_marks')} />
            )}
          </FormField>
          <FormField error={form.formState.errors.passing_marks?.message} label="Default passing marks">
            {({ id, describedBy }) => (
              <Input id={id} aria-describedby={describedBy} min="0" step="0.01" type="number" {...form.register('passing_marks')} />
            )}
          </FormField>
        </div>
        <FormField error={form.formState.errors.description?.message} label="Description">
          {({ id, describedBy }) => (
            <textarea
              className="min-h-20 rounded-lg border border-input bg-white px-3 py-2 text-sm"
              id={id}
              aria-describedby={describedBy}
              {...form.register('description')}
            />
          )}
        </FormField>
        <div className="flex justify-end gap-2">
          <Button onClick={() => onOpenChange(false)} type="button" variant="outline">Cancel</Button>
          <Button disabled={mutation.isPending} type="submit">{mutation.isPending ? 'Saving…' : 'Save subject'}</Button>
        </div>
      </form>
    </FormDialog>
  )
}

export function SubjectsPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [activeFilter, setActiveFilter] = useState('')
  const [page, setPage] = useState(1)
  const [editingSubject, setEditingSubject] = useState<Subject | null>(null)
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const query = useQuery({
    queryKey: ['subjects', { search, activeFilter, page, limit: 10 }],
    queryFn: () => schoolApi.subjects.list(
      { page, limit: 10, sort_by: 'name', sort_order: 'asc' },
      {
        search: search || undefined,
        active: activeFilter === '' ? undefined : activeFilter === 'true',
      },
    ),
  })
  const stateMutation = useMutation({
    mutationFn: (subject: Subject) =>
      subject.is_active
        ? schoolApi.subjects.deactivate(subject.id)
        : schoolApi.subjects.activate(subject.id),
    onSuccess: async (_result, subject) => {
      setSuccessMessage(subject.is_active ? 'Subject deactivated.' : 'Subject activated.')
      setErrorMessage(null)
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['subjects'] }),
        queryClient.invalidateQueries({ queryKey: ['classes'] }),
      ])
    },
    onError: (error) => setErrorMessage(toApiError(error).message),
  })
  const canEdit = user?.permissions?.includes('subjects.update') ?? false
  const canDelete = user?.permissions?.includes('subjects.delete') ?? false
  const columns = [
    { id: 'code', header: 'Code', cell: (subject: Subject) => <span className="font-semibold">{subject.code}</span> },
    { id: 'name', header: 'Subject', cell: (subject: Subject) => subject.name },
    { id: 'category', header: 'Category', cell: (subject: Subject) => subject.category || '—' },
    { id: 'type', header: 'Type', cell: (subject: Subject) => subject.subject_type },
    { id: 'status', header: 'Status', cell: (subject: Subject) => <StatusBadge status={subject.is_active ? 'active' : 'inactive'} /> },
    { id: 'actions', header: 'Actions', cell: (subject: Subject) => (
      <div className="flex flex-wrap gap-2">
        {canEdit ? (
          <>
            <Button onClick={() => {
              setEditingSubject(subject)
              setErrorMessage(null)
            }} size="sm" variant="ghost">Edit</Button>
            {!subject.is_active ? (
              <Button
                disabled={stateMutation.isPending}
                onClick={() => {
                  setErrorMessage(null)
                  stateMutation.mutate(subject)
                }}
                size="sm"
                variant="outline"
              >
                Activate
              </Button>
            ) : null}
          </>
        ) : null}
        {canDelete && subject.is_active ? (
          <ConfirmDialog
            confirmLabel="Deactivate subject"
            description="A subject offered to an active class cannot be deactivated."
            onConfirm={async () => {
              await stateMutation.mutateAsync(subject)
            }}
            title={`Deactivate ${subject.code}?`}
            destructive
            trigger={<Button size="sm" variant="outline">Deactivate</Button>}
          />
        ) : null}
      </div>
    ) },
  ]

  return (
    <>
      <PageHeader
        actions={
          <PermissionGate anyOf={['subjects.create']}>
            <Button onClick={() => {
              setEditingSubject(null)
              setIsCreateOpen(true)
              setErrorMessage(null)
            }}>Add subject</Button>
          </PermissionGate>
        }
        description="Maintain the subject catalog. Add class-specific subject offerings from Class Management."
        title="Subjects"
      />
      {successMessage ? <SuccessState title="Subject updated" description={successMessage} /> : null}
      {errorMessage ? (
        <Alert className="mt-4" variant="destructive">
          <AlertTitle>Subject operation failed</AlertTitle>
          <AlertDescription>{errorMessage}</AlertDescription>
        </Alert>
      ) : null}
      <div className="mt-5">
        <RecordList
          columns={columns}
          emptyMessage="No subjects match these filters."
          error={query.error ? toApiError(query.error).message : undefined}
          getRowId={(subject) => subject.id}
          isLoading={query.isLoading}
          onPageChange={setPage}
          onRetry={() => void query.refetch()}
          pagination={query.data?.pagination}
          rows={query.data?.items ?? []}
          toolbar={
            <div className="flex flex-col gap-3 sm:flex-row">
              <SearchField
                label="Search subjects by code or name"
                onChange={(value) => {
                  setSearch(value)
                  setPage(1)
                }}
                placeholder="Search code or name"
                value={search}
              />
              <label className="sr-only" htmlFor="subject-active">Filter active status</label>
              <select
                className="h-10 rounded-lg border border-input bg-white px-3 text-sm"
                id="subject-active"
                onChange={(event) => {
                  setActiveFilter(event.target.value)
                  setPage(1)
                }}
                value={activeFilter}
              >
                <option value="">All statuses</option>
                <option value="true">Active</option>
                <option value="false">Inactive</option>
              </select>
            </div>
          }
        />
      </div>
      <SubjectFormDialog
        key={`${editingSubject?.id ?? 'new'}-${isCreateOpen || editingSubject !== null}`}
        onOpenChange={(open) => {
          setIsCreateOpen(open)
          if (!open) setEditingSubject(null)
        }}
        open={isCreateOpen || editingSubject !== null}
        subject={editingSubject}
      />
    </>
  )
}
