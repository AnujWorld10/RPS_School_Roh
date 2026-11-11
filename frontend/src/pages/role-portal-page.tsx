import { useState, type FormEvent, type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { EmptyState, ErrorState, LoadingState, SuccessState } from '@/components/ui/async-state'
import { PageHeader } from '@/components/ui/page-header'
import { useAuth } from '@/features/auth/auth-context'
import {
  rolePortalApi,
  type EventCreate,
  type SchoolAssessment,
  type SchoolAssignment,
  type SchoolEvent,
  type TimetableEntry,
} from '@/features/school/role-portal-api'
import { schoolApi } from '@/features/school/school-api'
import type { Student } from '@/features/school/school-api'
import { toApiError } from '@/lib/api/api-error'

const queryKeys = {
  students: ['role-portal', 'students'],
  teachingAssignments: ['role-portal', 'teaching-assignments'],
  assignments: ['role-portal', 'assignments'],
  timetable: ['role-portal', 'timetable'],
  assessments: ['role-portal', 'assessments'],
  events: ['role-portal', 'events'],
}

function usePortalQueries(isTeacher: boolean) {
  const { user } = useAuth()
  const canRead = (permission: string) => user?.permissions?.includes(permission) ?? false
  const students = useQuery({
    queryKey: queryKeys.students,
    queryFn: () =>
      schoolApi.students.list(
        { page: 1, limit: 100, sort_by: 'first_name', sort_order: 'asc' },
        {},
      ),
    enabled: canRead('students.read'),
  })
  const teachingAssignments = useQuery({
    queryKey: queryKeys.teachingAssignments,
    queryFn: rolePortalApi.teachingAssignments.list,
    enabled: isTeacher,
  })
  const classes = useQuery({
    queryKey: ['role-portal', 'classes'],
    queryFn: async () =>
      (await schoolApi.classes.list(
        { page: 1, limit: 100, sort_by: 'name', sort_order: 'asc' },
        { status: 'active' },
      )).items,
    enabled: isTeacher,
  })
  const assignments = useQuery({
    queryKey: queryKeys.assignments,
    queryFn: rolePortalApi.assignments.list,
    enabled: canRead('assignments.read'),
  })
  const timetable = useQuery({
    queryKey: queryKeys.timetable,
    queryFn: rolePortalApi.timetable.list,
    enabled: canRead('timetable.read'),
  })
  const assessments = useQuery({
    queryKey: queryKeys.assessments,
    queryFn: rolePortalApi.assessments.list,
    enabled: canRead('assessments.read'),
  })
  const events = useQuery({
    queryKey: queryKeys.events,
    queryFn: rolePortalApi.events.list,
    enabled: canRead('events.read'),
  })
  return { students, teachingAssignments, classes, assignments, timetable, assessments, events }
}

function formatDay(day: number) {
  return ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day] ?? '—'
}

function StudentPortal({
  role,
  students,
  assignments,
  timetable,
  assessments,
  events,
}: {
  role: 'student' | 'parent'
  students: Student[]
  assignments: SchoolAssignment[]
  timetable: TimetableEntry[]
  assessments: SchoolAssessment[]
  events: SchoolEvent[]
}) {
  const [attachmentError, setAttachmentError] = useState('')
  return (
    <>
      <PageHeader
        title={role === 'parent' ? 'Parent portal' : 'Student portal'}
        description={
          role === 'parent'
            ? 'View the school information and learning updates for children linked to your account.'
            : 'View your school profile, assignments, timetable, assessments, and school events.'
        }
      />
      <div className="grid gap-5">
        <Card>
          <CardHeader>
            <CardTitle>{role === 'parent' ? 'Linked students' : 'My profile'}</CardTitle>
            <CardDescription>
              {role === 'parent'
                ? 'Student records are linked using the registered parent email and mobile number.'
                : 'Only student records matching your registered school email are shown.'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {students.length ? (
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {students.map((student) => (
                  <article className="rounded-xl border border-border bg-background p-4" key={student.id}>
                    <h2 className="font-semibold text-slate-950">
                      {student.first_name} {student.last_name}
                    </h2>
                    <dl className="mt-3 grid gap-2 text-sm text-slate-600">
                      <div className="flex justify-between gap-3">
                        <dt>Admission number</dt><dd>{student.admission_no || 'Not assigned'}</dd>
                      </div>
                      <div className="flex justify-between gap-3">
                        <dt>Current class ID</dt><dd>{student.current_class_id ?? 'Not assigned'}</dd>
                      </div>
                      <div className="flex justify-between gap-3">
                        <dt>Date of birth</dt><dd>{student.date_of_birth}</dd>
                      </div>
                      {student.email ? (
                        <div className="flex justify-between gap-3">
                          <dt>Email</dt><dd className="break-all text-right">{student.email}</dd>
                        </div>
                      ) : null}
                      {student.phone ? (
                        <div className="flex justify-between gap-3">
                          <dt>Mobile</dt><dd>{student.phone}</dd>
                        </div>
                      ) : null}
                      <div className="flex justify-between gap-3">
                        <dt>Status</dt><dd className="capitalize">{student.status}</dd>
                      </div>
                    </dl>
                  </article>
                ))}
              </div>
            ) : (
              <EmptyState
                title="No linked student profile"
                description="Ask the school office to confirm the student contact details and account link."
              />
            )}
          </CardContent>
        </Card>

        <div className="grid gap-5 xl:grid-cols-2">
          <DataCard title="Assignments" empty="No published assignments are available.">
            {assignments.map((assignment) => (
              <article className="border-b border-border py-3 last:border-0" key={assignment.id}>
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <h3 className="font-medium text-slate-900">{assignment.title}</h3>
                  <span className="text-xs text-slate-500">Due {assignment.due_date}</span>
                </div>
                <p className="mt-1 whitespace-pre-wrap text-sm text-slate-600">{assignment.details}</p>
                {assignment.attachments.map((file) => (
                  <button
                    className="mt-2 block text-left text-xs font-medium text-teal-800 underline hover:text-teal-950"
                    key={file.id}
                    onClick={() => {
                      void rolePortalApi.assignments.downloadAttachment(assignment.id, file.id).then((blob) => {
                        const url = URL.createObjectURL(blob)
                        const link = document.createElement('a')
                        link.href = url
                        link.download = file.file_name
                        link.click()
                        URL.revokeObjectURL(url)
                      }).catch((error: unknown) => setAttachmentError(toApiError(error).message))
                    }}
                    type="button"
                  >
                    Download {file.file_name}
                  </button>
                ))}
              </article>
            ))}
          </DataCard>
          <DataCard title="Assessments and results" empty="No published assessments are available.">
            {assessments.map((assessment) => (
              <article className="border-b border-border py-3 last:border-0" key={assessment.id}>
                <h3 className="font-medium text-slate-900">{assessment.name}</h3>
                <p className="mt-1 text-sm text-slate-600">
                  {assessment.assessment_type.replaceAll('_', ' ')} · {assessment.assessment_date} · Max {assessment.max_score}
                </p>
                {assessment.results.map((result) => (
                  <p className="mt-1 text-sm font-medium text-teal-900" key={result.id}>
                    {result.result_status === 'absent' ? 'Absent' : `Score: ${result.score}`}
                    {result.remarks ? ` · ${result.remarks}` : ''}
                  </p>
                ))}
              </article>
            ))}
          </DataCard>
          <DataCard title="Timetable" empty="No timetable periods are available.">
            {timetable.map((entry) => (
              <div className="flex flex-wrap justify-between gap-2 border-b border-border py-3 text-sm last:border-0" key={entry.id}>
                <span className="font-medium text-slate-900">{formatDay(entry.day_of_week)}</span>
                <span className="text-slate-600">{entry.start_time.slice(0, 5)}–{entry.end_time.slice(0, 5)}</span>
                <span className="text-slate-600">Class {entry.class_id} · Subject {entry.subject_id}</span>
              </div>
            ))}
          </DataCard>
          <DataCard title="School events" empty="No school events are available.">
            {events.map((event) => (
              <article className="border-b border-border py-3 last:border-0" key={event.id}>
                <h3 className="font-medium text-slate-900">{event.title}</h3>
                <p className="mt-1 text-sm text-slate-600">{new Date(event.starts_at).toLocaleString()}</p>
                <p className="mt-1 text-sm text-slate-600">{event.description}</p>
              </article>
            ))}
          </DataCard>
        </div>
        {attachmentError ? (
          <ErrorState title="Attachment download failed" description={attachmentError} />
        ) : null}
      </div>
    </>
  )
}

function DataCard({
  title,
  empty,
  children,
}: {
  title: string
  empty: string
  children: ReactNode
}) {
  const isEmpty = Array.isArray(children) ? children.length === 0 : !children
  return (
    <Card>
      <CardHeader><CardTitle>{title}</CardTitle></CardHeader>
      <CardContent>
        {isEmpty ? (
          <p className="text-sm text-slate-500">{empty}</p>
        ) : children}
      </CardContent>
    </Card>
  )
}

export function RolePortalPage({ role }: { role: 'student' | 'parent' | 'teacher' }) {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const isTeacher = role === 'teacher'
  const data = usePortalQueries(isTeacher)
  const [statusMessage, setStatusMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [saving, setSaving] = useState(false)
  const [mappingClassId, setMappingClassId] = useState('')
  const [mappingSubjectId, setMappingSubjectId] = useState('')
  const subjectsForClass = useQuery({
    queryKey: ['role-portal', 'class-subjects', mappingClassId],
    queryFn: () => schoolApi.classes.subjects(Number(mappingClassId)),
    enabled: Boolean(mappingClassId),
  })

  const invalidate = async (...keys: (readonly string[])[]) => {
    await Promise.all(keys.map((queryKey) => queryClient.invalidateQueries({ queryKey })))
  }

  async function runOperation(
    action: () => Promise<unknown>,
    message: string,
    keys: (readonly string[])[],
    form?: HTMLFormElement,
  ) {
    setSaving(true)
    setErrorMessage('')
    setStatusMessage('')
    try {
      await action()
      await invalidate(...keys)
      setStatusMessage(message)
      form?.reset()
    } catch (error) {
      setErrorMessage(toApiError(error).message)
    } finally {
      setSaving(false)
    }
  }

  function submit(
    event: FormEvent<HTMLFormElement>,
    action: (form: FormData) => Promise<unknown>,
    message: string,
    keys: (readonly string[])[],
  ) {
    event.preventDefault()
    const form = event.currentTarget
    return runOperation(() => action(new FormData(form)), message, keys, form)
  }

  const assignments = data.assignments.data ?? []
  const timetable = data.timetable.data ?? []
  const assessments = data.assessments.data ?? []
  const events = data.events.data ?? []
  const students = data.students.data?.items ?? []
  const teachingAssignments = data.teachingAssignments.data ?? []
  const currentRoles = user?.roles ?? []
  const loadErrors = [
    data.students.error,
    data.teachingAssignments.error,
    data.classes.error,
    data.assignments.error,
    data.timetable.error,
    data.assessments.error,
    data.events.error,
  ].filter(Boolean)

  if (
    data.students.isPending
    || data.assignments.isPending
    || data.timetable.isPending
    || data.assessments.isPending
    || data.events.isPending
    || (isTeacher && (data.teachingAssignments.isPending || data.classes.isPending))
  ) {
    return <LoadingState label="Loading your school portal" />
  }
  if (loadErrors.length) {
    return (
      <ErrorState
        description={toApiError(loadErrors[0]).message}
        onRetry={() => void Promise.all([
          data.students.refetch(),
          data.teachingAssignments.refetch(),
          data.classes.refetch(),
          data.assignments.refetch(),
          data.timetable.refetch(),
          data.assessments.refetch(),
          data.events.refetch(),
        ])}
        title="Portal data could not be loaded"
      />
    )
  }

  if (!isTeacher) {
    return (
      <StudentPortal
        assignments={assignments}
        assessments={assessments}
        events={events.filter((event) => event.status === 'published')}
        role={role}
        students={students}
        timetable={timetable}
      />
    )
  }

  const isAdmin = currentRoles.includes('ADMIN') || currentRoles.includes('SUPER_ADMIN')
  const activeClasses = data.classes.data ?? []
  const mappedOptions = teachingAssignments.map((item) => ({
    value: `${item.class_id}:${item.subject_id}`,
    label: `${item.class_name} · ${item.subject_name}`,
  }))

  return (
    <>
      <PageHeader
        title="Teacher workspace"
        description="Manage academic work, review student records, and send school events for administrator review."
        actions={<Link className="text-sm font-semibold text-teal-800 hover:underline" to="/students">Manage students</Link>}
      />
      {statusMessage ? <div className="mb-5"><SuccessState title="Saved" description={statusMessage} /></div> : null}
      {errorMessage ? <div className="mb-5"><ErrorState description={errorMessage} title="Could not save changes" /></div> : null}
      <div className="mb-5 flex flex-wrap gap-2">
        <Link className="rounded-lg border border-border bg-white px-3 py-2 text-sm font-medium text-teal-900 hover:bg-teal-50" to="/inquiries">Review inquiries</Link>
        <Link className="rounded-lg border border-border bg-white px-3 py-2 text-sm font-medium text-teal-900 hover:bg-teal-50" to="/admissions">Review admissions</Link>
        <Link className="rounded-lg border border-border bg-white px-3 py-2 text-sm font-medium text-teal-900 hover:bg-teal-50" to="/subjects">Manage subjects</Link>
        <Link className="rounded-lg border border-border bg-white px-3 py-2 text-sm font-medium text-teal-900 hover:bg-teal-50" to="/events">School events</Link>
      </div>
      <div className="grid gap-5 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>My class and subject mappings</CardTitle>
            <CardDescription>You can map or remove only your own teaching assignments. Existing class subject offerings are required.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {teachingAssignments.map((item) => (
              <div className="flex items-center justify-between gap-3 border-b border-border py-2 text-sm" key={`${item.class_id}:${item.subject_id}`}>
                <span>{item.class_name} · {item.subject_name}</span>
                <button
                  className="text-sm font-medium text-destructive underline-offset-2 hover:underline"
                  disabled={saving}
                  onClick={() => void runOperation(
                    () => rolePortalApi.teachingAssignments.remove(item.class_id, item.subject_id),
                    'Your class and subject mapping was removed.',
                    [queryKeys.teachingAssignments],
                  )}
                  type="button"
                >
                  Remove
                </button>
              </div>
            ))}
            <form
              className="grid gap-3 sm:grid-cols-2"
              onSubmit={(event) => void submit(
                event,
                (form) => rolePortalApi.teachingAssignments.add(
                  Number(form.get('class_id')),
                  Number(form.get('subject_id')),
                ),
                'Your teaching assignment was added.',
                [queryKeys.teachingAssignments],
              )}
            >
              <label className="grid gap-1 text-sm font-medium" htmlFor="mapping-class">Class</label>
              <select
                className="min-h-10 rounded-lg border border-input bg-background px-3 text-sm"
                id="mapping-class"
                name="class_id"
                onChange={(event) => {
                  setMappingClassId(event.target.value)
                  setMappingSubjectId('')
                }}
                required
                value={mappingClassId}
              >
                <option value="">Select a class</option>
                {activeClasses.map((schoolClass) => (
                  <option key={schoolClass.id} value={schoolClass.id}>{schoolClass.name} {schoolClass.section}</option>
                ))}
              </select>
              <label className="grid gap-1 text-sm font-medium" htmlFor="mapping-subject">Subject offered to class</label>
              <select
                className="min-h-10 rounded-lg border border-input bg-background px-3 text-sm"
                id="mapping-subject"
                name="subject_id"
                onChange={(event) => setMappingSubjectId(event.target.value)}
                required
                value={mappingSubjectId}
              >
                <option value="">Select a subject</option>
                {(subjectsForClass.data ?? []).map((subject) => (
                  <option key={subject.id} value={subject.id}>{subject.name}</option>
                ))}
              </select>
              <button className="min-h-10 rounded-lg bg-primary px-4 text-sm font-semibold text-primary-foreground disabled:opacity-50 sm:col-span-2" disabled={saving || !mappingClassId || !mappingSubjectId} type="submit">
                Add my mapping
              </button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Create assignment</CardTitle><CardDescription>Assignments start as drafts and are hidden from students until published.</CardDescription></CardHeader>
          <CardContent>
            <form className="grid gap-3" onSubmit={(event) => void submit(
              event,
              async (form) => {
                const [selectedClassId, selectedSubjectId] = String(form.get('teaching_assignment')).split(':').map(Number)
                const assignment = await rolePortalApi.assignments.create({
                  title: String(form.get('title')),
                  details: String(form.get('details')),
                  class_id: selectedClassId,
                  subject_id: selectedSubjectId,
                  due_date: String(form.get('due_date')),
                })
                const file = form.get('attachment')
                if (file instanceof File && file.size > 0) {
                  try {
                    await rolePortalApi.assignments.uploadAttachment(assignment.id, file)
                  } catch (error) {
                    throw new Error(
                      `Assignment saved as a draft, but the attachment failed to upload: ${toApiError(error).message}`,
                      { cause: error },
                    )
                  }
                }
              },
              'Assignment saved as a draft.',
              [queryKeys.assignments],
            )}>
              <label className="grid gap-1 text-sm font-medium" htmlFor="assignment-title">Title</label>
              <input className="min-h-10 rounded-lg border border-input px-3 text-sm" id="assignment-title" maxLength={200} name="title" required />
              <label className="grid gap-1 text-sm font-medium" htmlFor="assignment-details">Instructions</label>
              <textarea className="min-h-24 rounded-lg border border-input px-3 py-2 text-sm" id="assignment-details" maxLength={10000} name="details" required />
              <label className="grid gap-1 text-sm font-medium" htmlFor="assignment-mapping">Class and subject</label>
              <select className="min-h-10 rounded-lg border border-input px-3 text-sm" id="assignment-mapping" name="teaching_assignment" required>
                <option value="">Select mapped class and subject</option>
                {mappedOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
              </select>
              <label className="grid gap-1 text-sm font-medium" htmlFor="assignment-due-date">Due date</label>
              <input className="min-h-10 rounded-lg border border-input px-3 text-sm" id="assignment-due-date" name="due_date" type="date" required />
              <label className="grid gap-1 text-sm font-medium" htmlFor="assignment-attachment">Optional attachment (PDF, JPG, JPEG, PNG; configured size limit)</label>
              <input accept=".pdf,.jpg,.jpeg,.png" className="min-h-10 rounded-lg border border-input px-3 py-2 text-sm" id="assignment-attachment" name="attachment" type="file" />
              <button className="min-h-10 rounded-lg bg-primary px-4 text-sm font-semibold text-primary-foreground disabled:opacity-50" disabled={saving} type="submit">Save draft</button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Assignments</CardTitle><CardDescription>Publish a draft when it is ready for students.</CardDescription></CardHeader>
          <CardContent className="space-y-3">
            {assignments.length ? assignments.map((assignment) => (
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border py-3" key={assignment.id}>
                <div><p className="font-medium">{assignment.title}</p><p className="text-sm text-muted-foreground">{assignment.status} · due {assignment.due_date}</p></div>
                {assignment.status === 'draft' ? <button className="rounded-lg border border-teal-200 px-3 py-2 text-sm font-semibold text-teal-900 hover:bg-teal-50" disabled={saving} onClick={() => void runOperation(() => rolePortalApi.assignments.publish(assignment.id), 'Assignment published.', [queryKeys.assignments])} type="button">Publish</button> : null}
              </div>
            )) : <p className="text-sm text-muted-foreground">No assignments have been created.</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Create assessment</CardTitle><CardDescription>Assessments remain unpublished until you publish them.</CardDescription></CardHeader>
          <CardContent>
            <form className="grid gap-3" onSubmit={(event) => void submit(
              event,
              (form) => {
                const [selectedClassId, selectedSubjectId] = String(form.get('teaching_assignment')).split(':').map(Number)
                return rolePortalApi.assessments.create({
                  name: String(form.get('name')),
                  assessment_type: form.get('assessment_type') as 'unit_test' | 'periodic_test' | 'mid_term' | 'final_exam' | 'assignment' | 'quiz' | 'practical' | 'oral',
                  class_id: selectedClassId,
                  subject_id: selectedSubjectId,
                  assessment_date: String(form.get('assessment_date')),
                  max_score: Number(form.get('max_score')),
                })
              },
              'Assessment created as unpublished.',
              [queryKeys.assessments],
            )}>
              <label className="grid gap-1 text-sm font-medium" htmlFor="assessment-name">Assessment name</label>
              <input className="min-h-10 rounded-lg border border-input px-3 text-sm" id="assessment-name" maxLength={200} name="name" required />
              <label className="grid gap-1 text-sm font-medium" htmlFor="assessment-type">Type</label>
              <select className="min-h-10 rounded-lg border border-input px-3 text-sm" id="assessment-type" name="assessment_type">
                {['unit_test', 'periodic_test', 'mid_term', 'final_exam', 'assignment', 'quiz', 'practical', 'oral'].map((type) => <option key={type} value={type}>{type.replaceAll('_', ' ')}</option>)}
              </select>
              <label className="grid gap-1 text-sm font-medium" htmlFor="assessment-mapping">Class and subject</label>
              <select className="min-h-10 rounded-lg border border-input px-3 text-sm" id="assessment-mapping" name="teaching_assignment" required>
                <option value="">Select mapped class and subject</option>
                {mappedOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
              </select>
              <label className="grid gap-1 text-sm font-medium" htmlFor="assessment-date">Date</label>
              <input className="min-h-10 rounded-lg border border-input px-3 text-sm" id="assessment-date" name="assessment_date" type="date" required />
              <label className="grid gap-1 text-sm font-medium" htmlFor="assessment-max-score">Maximum score</label>
              <input className="min-h-10 rounded-lg border border-input px-3 text-sm" id="assessment-max-score" min="0.01" name="max_score" step="0.01" type="number" required />
              <button className="min-h-10 rounded-lg bg-primary px-4 text-sm font-semibold text-primary-foreground disabled:opacity-50" disabled={saving} type="submit">Create assessment</button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Enter student results</CardTitle><CardDescription>Scores are limited to the assessment maximum; absent students are recorded without a score.</CardDescription></CardHeader>
          <CardContent>
            <form className="grid gap-3" onSubmit={(event) => void submit(
              event,
              (form) => {
                const status = String(form.get('result_status')) as 'present' | 'absent'
                const scoreValue = String(form.get('score') ?? '')
                return rolePortalApi.assessments.saveResult(
                  Number(form.get('assessment_id')),
                  Number(form.get('student_id')),
                  { score: status === 'absent' || !scoreValue ? null : Number(scoreValue), result_status: status },
                )
              },
              'Student result saved.',
              [queryKeys.assessments],
            )}>
              <label className="grid gap-1 text-sm font-medium" htmlFor="result-assessment">Assessment</label>
              <select className="min-h-10 rounded-lg border border-input px-3 text-sm" id="result-assessment" name="assessment_id" required>
                <option value="">Select an unpublished assessment</option>
                {assessments.filter((assessment) => !assessment.is_published).map((assessment) => <option key={assessment.id} value={assessment.id}>{assessment.name}</option>)}
              </select>
              <label className="grid gap-1 text-sm font-medium" htmlFor="result-student">Student</label>
              <select className="min-h-10 rounded-lg border border-input px-3 text-sm" id="result-student" name="student_id" required>
                <option value="">Select a student</option>
                {students.map((student) => <option key={student.id} value={student.id}>{student.first_name} {student.last_name} · {student.admission_no || student.id}</option>)}
              </select>
              <label className="grid gap-1 text-sm font-medium" htmlFor="result-status">Attendance</label>
              <select className="min-h-10 rounded-lg border border-input px-3 text-sm" id="result-status" name="result_status">
                <option value="present">Present</option><option value="absent">Absent</option>
              </select>
              <label className="grid gap-1 text-sm font-medium" htmlFor="result-score">Score (required when present)</label>
              <input className="min-h-10 rounded-lg border border-input px-3 text-sm" id="result-score" min="0" name="score" step="0.01" type="number" />
              <button className="min-h-10 rounded-lg bg-primary px-4 text-sm font-semibold text-primary-foreground disabled:opacity-50" disabled={saving} type="submit">Save result</button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Assessments</CardTitle><CardDescription>Review recorded results before publishing.</CardDescription></CardHeader>
          <CardContent className="space-y-3">
            {assessments.length ? assessments.map((assessment) => (
              <div className="border-b border-border py-3 last:border-0" key={assessment.id}>
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div><p className="font-medium">{assessment.name}</p><p className="text-sm text-muted-foreground">{assessment.assessment_type.replaceAll('_', ' ')} · max {assessment.max_score} · {assessment.is_published ? 'published' : 'unpublished'}</p></div>
                  {!assessment.is_published ? <button className="rounded-lg border border-teal-200 px-3 py-2 text-sm font-semibold text-teal-900 hover:bg-teal-50" disabled={saving} onClick={() => void runOperation(() => rolePortalApi.assessments.publish(assessment.id), 'Assessment published.', [queryKeys.assessments])} type="button">Publish results</button> : null}
                </div>
                <p className="mt-2 text-sm text-slate-600">{assessment.results.length} result(s) entered.</p>
              </div>
            )) : <p className="text-sm text-muted-foreground">No assessments have been created.</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Create timetable period</CardTitle><CardDescription>Periods that overlap for a class or teacher are rejected by the API.</CardDescription></CardHeader>
          <CardContent>
            <form className="grid gap-3 sm:grid-cols-2" onSubmit={(event) => void submit(
              event,
              (form) => {
                const [selectedClassId, selectedSubjectId] = String(form.get('teaching_assignment')).split(':').map(Number)
                return rolePortalApi.timetable.create({
                  class_id: selectedClassId,
                  subject_id: selectedSubjectId,
                  day_of_week: Number(form.get('day_of_week')),
                  start_time: String(form.get('start_time')),
                  end_time: String(form.get('end_time')),
                  room: String(form.get('room') || ''),
                  academic_year: String(form.get('academic_year')),
                })
              },
              'Timetable period saved.',
              [queryKeys.timetable],
            )}>
              <label className="grid gap-1 text-sm font-medium" htmlFor="timetable-mapping">Class and subject</label>
              <select className="min-h-10 rounded-lg border border-input px-3 text-sm" id="timetable-mapping" name="teaching_assignment" required>
                <option value="">Select mapped class and subject</option>
                {mappedOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
              </select>
              <label className="grid gap-1 text-sm font-medium" htmlFor="timetable-day">Weekday</label>
              <select className="min-h-10 rounded-lg border border-input px-3 text-sm" id="timetable-day" name="day_of_week">{['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].map((day, index) => <option key={day} value={index}>{day}</option>)}</select>
              <label className="grid gap-1 text-sm font-medium" htmlFor="timetable-start">Start time</label>
              <input className="min-h-10 rounded-lg border border-input px-3 text-sm" id="timetable-start" name="start_time" type="time" required />
              <label className="grid gap-1 text-sm font-medium" htmlFor="timetable-end">End time</label>
              <input className="min-h-10 rounded-lg border border-input px-3 text-sm" id="timetable-end" name="end_time" type="time" required />
              <label className="grid gap-1 text-sm font-medium" htmlFor="timetable-room">Room (optional)</label>
              <input className="min-h-10 rounded-lg border border-input px-3 text-sm" id="timetable-room" maxLength={100} name="room" />
              <label className="grid gap-1 text-sm font-medium" htmlFor="timetable-year">Academic year</label>
              <input className="min-h-10 rounded-lg border border-input px-3 text-sm" defaultValue={activeClasses[0]?.academic_year} id="timetable-year" maxLength={20} name="academic_year" required />
              <button className="min-h-10 rounded-lg bg-primary px-4 text-sm font-semibold text-primary-foreground disabled:opacity-50 sm:col-span-2" disabled={saving} type="submit">Save timetable period</button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Timetable</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {timetable.map((entry) => <p className="border-b border-border py-2 text-sm" key={entry.id}>{formatDay(entry.day_of_week)} · {entry.start_time.slice(0, 5)}–{entry.end_time.slice(0, 5)} · class {entry.class_id} · subject {entry.subject_id}</p>)}
            {!timetable.length ? <p className="text-sm text-muted-foreground">No timetable periods have been set.</p> : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Propose a school event</CardTitle><CardDescription>Teacher events remain unpublished until an administrator reviews them.</CardDescription></CardHeader>
          <CardContent>
            <form className="grid gap-3" onSubmit={(event) => void submit(
              event,
              (form) => rolePortalApi.events.create({
                title: String(form.get('title')),
                description: String(form.get('description')),
                starts_at: new Date(String(form.get('starts_at'))).toISOString(),
                ends_at: new Date(String(form.get('ends_at'))).toISOString(),
                venue: String(form.get('venue') || ''),
                audience: String(form.get('audience')) as EventCreate['audience'],
              }),
              'Event proposal submitted for administrator review.',
              [queryKeys.events],
            )}>
              <label className="grid gap-1 text-sm font-medium" htmlFor="event-title">Title</label>
              <input className="min-h-10 rounded-lg border border-input px-3 text-sm" id="event-title" maxLength={200} name="title" required />
              <label className="grid gap-1 text-sm font-medium" htmlFor="event-description">Description</label>
              <textarea className="min-h-20 rounded-lg border border-input px-3 py-2 text-sm" id="event-description" maxLength={10000} name="description" required />
              <label className="grid gap-1 text-sm font-medium" htmlFor="event-start">Start date and time (your device’s local time)</label>
              <input className="min-h-10 rounded-lg border border-input px-3 text-sm" id="event-start" name="starts_at" type="datetime-local" required />
              <label className="grid gap-1 text-sm font-medium" htmlFor="event-end">End date and time (your device’s local time)</label>
              <input className="min-h-10 rounded-lg border border-input px-3 text-sm" id="event-end" name="ends_at" type="datetime-local" required />
              <label className="grid gap-1 text-sm font-medium" htmlFor="event-venue">Venue (optional)</label>
              <input className="min-h-10 rounded-lg border border-input px-3 text-sm" id="event-venue" maxLength={200} name="venue" />
              <label className="grid gap-1 text-sm font-medium" htmlFor="event-audience">Audience</label>
              <select className="min-h-10 rounded-lg border border-input px-3 text-sm" id="event-audience" name="audience"><option value="all">Students and parents</option><option value="students">Students</option><option value="parents">Parents</option><option value="public">Public</option></select>
              <button className="min-h-10 rounded-lg bg-primary px-4 text-sm font-semibold text-primary-foreground disabled:opacity-50" disabled={saving} type="submit">Submit event for review</button>
            </form>
          </CardContent>
        </Card>
      </div>
      <p className="sr-only" aria-live="polite">{statusMessage || errorMessage}</p>
      {isAdmin ? <p className="mt-5 text-xs text-muted-foreground">This account has Administration permissions in addition to the Teacher role.</p> : null}
    </>
  )
}

export function SchoolEventsPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const events = useQuery({ queryKey: queryKeys.events, queryFn: rolePortalApi.events.list })
  const [busyEventId, setBusyEventId] = useState<number | null>(null)
  const [errorMessage, setErrorMessage] = useState('')
  const [notice, setNotice] = useState('')
  const canReview = user?.permissions?.includes('events.review') ?? false

  async function review(eventId: number, decision: 'published' | 'rejected') {
    setBusyEventId(eventId)
    setErrorMessage('')
    setNotice('')
    try {
      await rolePortalApi.events.review(eventId, decision, decision === 'rejected' ? 'Not approved by Administration.' : undefined)
      await queryClient.invalidateQueries({ queryKey: queryKeys.events })
      setNotice(`Event ${decision}.`)
    } catch (error) {
      setErrorMessage(toApiError(error).message)
    } finally {
      setBusyEventId(null)
    }
  }

  return (
    <>
      <PageHeader title="School events" description="Published events are visible to their selected audience. Teacher proposals require administrator review." />
      {notice ? <div className="mb-4"><SuccessState title="Updated" description={notice} /></div> : null}
      {errorMessage ? <div className="mb-4"><ErrorState title="Event update failed" description={errorMessage} /></div> : null}
      {events.isPending ? <LoadingState label="Loading school events" /> : null}
      {events.error ? <ErrorState description={toApiError(events.error).message} onRetry={() => void events.refetch()} /> : null}
      {events.data?.length === 0 ? <EmptyState title="No school events" description="No published or pending events are available." /> : null}
      <div className="grid gap-4">
        {events.data?.map((event) => (
          <Card key={event.id}>
            <CardHeader>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div><CardTitle>{event.title}</CardTitle><CardDescription>{new Date(event.starts_at).toLocaleString()} · {event.venue || 'Venue to be announced'}</CardDescription></div>
                <span className="rounded-full bg-teal-50 px-3 py-1 text-xs font-semibold capitalize text-teal-900">{event.status.replaceAll('_', ' ')}</span>
              </div>
            </CardHeader>
            <CardContent>
              <p className="whitespace-pre-wrap text-sm text-slate-700">{event.description}</p>
              {event.rejection_reason ? <p className="mt-2 text-sm text-destructive">Reason: {event.rejection_reason}</p> : null}
              {canReview && event.status === 'pending_review' ? (
                <div className="mt-4 flex flex-wrap gap-2">
                  <button className="min-h-9 rounded-lg bg-primary px-3 text-sm font-semibold text-primary-foreground disabled:opacity-50" disabled={busyEventId === event.id} onClick={() => void review(event.id, 'published')} type="button">Approve and publish</button>
                  <button className="min-h-9 rounded-lg border border-destructive/30 px-3 text-sm font-semibold text-destructive disabled:opacity-50" disabled={busyEventId === event.id} onClick={() => void review(event.id, 'rejected')} type="button">Reject</button>
                </div>
              ) : null}
            </CardContent>
          </Card>
        ))}
      </div>
    </>
  )
}
