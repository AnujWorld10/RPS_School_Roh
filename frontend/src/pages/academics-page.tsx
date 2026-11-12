import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { ClassRecordSelector } from '@/components/school/class-record-selector'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/async-state'
import { Input } from '@/components/ui/input'
import { PageHeader } from '@/components/ui/page-header'
import {
  schoolApi,
  type AcademicMarkInput,
  type ClassSubjectOffering,
  type ExaminationComponentInput,
  type ExaminationRosterEntry,
} from '@/features/school/school-api'
import { toApiError } from '@/lib/api/api-error'

type DraftComponent = {
  name: string
  component_type: ExaminationComponentInput['component_type']
  max_marks: string
  passing_marks: string
}

type MarkValue = {
  status: AcademicMarkInput['status']
  obtained_marks: string
  remarks: string
}

const listParams = { page: 1, limit: 100, sort_by: 'name', sort_order: 'asc' as const }

function markKey(studentId: number, componentId: number) {
  return `${studentId}-${componentId}`
}

function OfferingSettings({
  offering,
  teachers,
  onSave,
  onAssignTeacher,
  busy,
}: {
  offering: ClassSubjectOffering
  teachers: Array<{ id: number; first_name: string; last_name: string }>
  onSave: (value: {
    subject_type: ClassSubjectOffering['subject_type']
    stream: string | null
    is_active: boolean
  }) => void
  onAssignTeacher: (teacherId: number) => void
  busy: boolean
}) {
  const [subjectType, setSubjectType] = useState(offering.subject_type)
  const [stream, setStream] = useState(offering.stream ?? '')
  const [isActive, setIsActive] = useState(offering.is_active)
  const [teacherId, setTeacherId] = useState(offering.teacher_id?.toString() ?? '')

  return (
    <tr className="border-t border-slate-100 align-top">
      <td className="px-3 py-3">
        <p className="font-medium text-slate-900">{offering.name}</p>
        <p className="text-xs text-slate-500">{offering.code}{offering.category ? ` · ${offering.category}` : ''}</p>
      </td>
      <td className="px-3 py-3">
        <select
          aria-label={`${offering.name} offering type`}
          className="h-9 rounded-lg border border-input bg-white px-2 text-sm"
          onChange={(event) => setSubjectType(event.target.value as ClassSubjectOffering['subject_type'])}
          value={subjectType}
        >
          <option value="mandatory">Mandatory</option>
          <option value="elective">Elective</option>
          <option value="optional">Optional</option>
        </select>
      </td>
      <td className="px-3 py-3">
        <Input
          aria-label={`${offering.name} stream`}
          className="min-w-24"
          onChange={(event) => setStream(event.target.value)}
          placeholder="Stream"
          value={stream}
        />
      </td>
      <td className="px-3 py-3">
        <select
          aria-label={`${offering.name} assigned teacher`}
          className="h-9 min-w-36 rounded-lg border border-input bg-white px-2 text-sm"
          onChange={(event) => setTeacherId(event.target.value)}
          value={teacherId}
        >
          <option value="">Not assigned</option>
          {teachers.map((teacher) => (
            <option key={teacher.id} value={teacher.id}>
              {teacher.first_name} {teacher.last_name}
            </option>
          ))}
        </select>
      </td>
      <td className="px-3 py-3">
        <label className="flex items-center gap-2 text-sm">
          <input checked={isActive} onChange={(event) => setIsActive(event.target.checked)} type="checkbox" />
          Active
        </label>
      </td>
      <td className="px-3 py-3">
        <div className="flex flex-wrap gap-2">
          <Button
            disabled={busy}
            onClick={() => onSave({
              subject_type: subjectType,
              stream: stream.trim() || null,
              is_active: isActive,
            })}
            size="sm"
            variant="outline"
          >
            Save offering
          </Button>
          <Button
            disabled={busy || !teacherId || Number(teacherId) === offering.teacher_id}
            onClick={() => onAssignTeacher(Number(teacherId))}
            size="sm"
            variant="ghost"
          >
            Assign teacher
          </Button>
        </div>
      </td>
    </tr>
  )
}

function formatPercent(value: number) {
  return `${Number(value).toFixed(2)}%`
}

export function AcademicsPage() {
  const queryClient = useQueryClient()
  const [selectedClassId, setSelectedClassId] = useState<number | null>(null)
  const [classSelectionIncomplete, setClassSelectionIncomplete] = useState(false)
  const [newSubjectId, setNewSubjectId] = useState('')
  const [newSubjectType, setNewSubjectType] = useState<ClassSubjectOffering['subject_type']>('mandatory')
  const [newStream, setNewStream] = useState('')
  const [selectedStudentId, setSelectedStudentId] = useState<number | null>(null)
  const [selectedExaminationId, setSelectedExaminationId] = useState<number | null>(null)
  const [examName, setExamName] = useState('')
  const [examType, setExamType] = useState('term')
  const [examStart, setExamStart] = useState('')
  const [examEnd, setExamEnd] = useState('')
  const [draftComponents, setDraftComponents] = useState<Record<number, DraftComponent[]>>({})
  const [markValues, setMarkValues] = useState<Record<string, MarkValue>>({})
  const [correctionReason, setCorrectionReason] = useState('')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const classesQuery = useQuery({
    queryKey: ['classes', 'academic-management'],
    queryFn: () => schoolApi.classes.list(listParams, { status: 'active' }),
  })
  const classes = useMemo(() => classesQuery.data?.items ?? [], [classesQuery.data?.items])
  const activeClassId = classSelectionIncomplete
    ? null
    : classes.some((item) => item.id === selectedClassId)
      ? selectedClassId
      : classes[0]?.id ?? null

  const offeringsQuery = useQuery({
    queryKey: ['academics', 'offerings', activeClassId],
    queryFn: () => schoolApi.academics.classSubjects(activeClassId!),
    enabled: activeClassId !== null,
  })
  const catalogQuery = useQuery({
    queryKey: ['subjects', 'academic-catalog'],
    queryFn: () => schoolApi.subjects.list(listParams, { active: true }),
  })
  const teachersQuery = useQuery({
    queryKey: ['teachers', 'academic-management'],
    queryFn: () => schoolApi.teachers.list(listParams, { status: 'active' }),
  })
  const studentsQuery = useQuery({
    queryKey: ['students', 'academic-electives', activeClassId],
    queryFn: () => schoolApi.students.list(listParams, {
      status: 'active',
      current_class_id: activeClassId!,
    }),
    enabled: activeClassId !== null,
  })
  const offerings = offeringsQuery.data ?? []
  const teachers = teachersQuery.data?.items ?? []
  const subjects = catalogQuery.data?.items ?? []
  const offeredIds = new Set(offerings.map((item) => item.subject_id))
  const availableSubjects = subjects.filter((item) => !offeredIds.has(item.id))

  const examinationsQuery = useQuery({
    queryKey: ['academics', 'examinations', activeClassId],
    queryFn: () => schoolApi.academics.examinations(activeClassId ?? undefined),
    enabled: activeClassId !== null,
  })
  const examinations = useMemo(
    () => examinationsQuery.data ?? [],
    [examinationsQuery.data],
  )
  const activeExaminationId = examinations.some((item) => item.id === selectedExaminationId)
    ? selectedExaminationId
    : examinations[0]?.id ?? null
  const selectedExamination = examinations.find((item) => item.id === activeExaminationId) ?? null
  const rosterQuery = useQuery({
    queryKey: ['academics', 'roster', activeExaminationId],
    queryFn: () => schoolApi.academics.examinationRoster(activeExaminationId!),
    enabled: activeExaminationId !== null,
  })
  const roster = rosterQuery.data ?? []
  const resultsQuery = useQuery({
    queryKey: ['academics', 'results', activeExaminationId],
    queryFn: () => schoolApi.academics.results(activeExaminationId!),
    enabled: activeExaminationId !== null
      && (selectedExamination?.status === 'published' || selectedExamination?.status === 'locked'),
  })
  const studentList = useMemo(
    () => studentsQuery.data?.items ?? [],
    [studentsQuery.data?.items],
  )
  const activeStudentId = studentList.some((student) => student.id === selectedStudentId)
    ? selectedStudentId
    : studentList[0]?.id ?? null
  const electiveQuery = useQuery({
    queryKey: ['academics', 'student-subjects', activeStudentId],
    queryFn: () => schoolApi.academics.studentSubjects(activeStudentId!),
    enabled: activeStudentId !== null,
  })
  const electiveSubjects = useMemo(() => electiveQuery.data ?? [], [electiveQuery.data])
  const chosenElectiveIds = useMemo(
    () => electiveSubjects.filter((item) => item.selected
      && (item.subject_type === 'elective' || item.subject_type === 'optional'))
      .map((item) => item.subject_id),
    [electiveSubjects],
  )
  const gradingQuery = useQuery({
    queryKey: ['academics', 'grading-scale', 'DEFAULT'],
    queryFn: () => schoolApi.academics.gradingScale('DEFAULT'),
  })
  const [gradingDraft, setGradingDraft] = useState<Array<{
    grade: string
    minimum_percentage: string
    maximum_percentage: string
    description: string
  }> | null>(null)
  const defaultGradingDraft = useMemo(
    () => gradingQuery.data?.map((rule) => ({
        grade: rule.grade,
        minimum_percentage: String(rule.minimum_percentage),
        maximum_percentage: String(rule.maximum_percentage),
        description: rule.description ?? '',
      })) ?? null,
    [gradingQuery.data],
  )
  const currentGradingDraft = gradingDraft ?? defaultGradingDraft

  const refreshAcademicData = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['academics'] }),
      queryClient.invalidateQueries({ queryKey: ['classes'] }),
      queryClient.invalidateQueries({ queryKey: ['subjects'] }),
      queryClient.invalidateQueries({ queryKey: ['students'] }),
    ])
  }
  const mutationOptions = {
    onError: (error: unknown) => {
      setSuccessMessage(null)
      setErrorMessage(toApiError(error).message)
    },
  }
  const configureOffering = useMutation({
    mutationFn: ({ subjectId, value }: {
      subjectId: number
      value: {
        subject_type: ClassSubjectOffering['subject_type']
        stream: string | null
        is_active: boolean
      }
    }) => schoolApi.academics.configureClassSubject(activeClassId!, subjectId, value),
    onSuccess: async () => {
      setErrorMessage(null)
      setSuccessMessage('Class subject offering saved.')
      await refreshAcademicData()
    },
    ...mutationOptions,
  })
  const assignTeacher = useMutation({
    mutationFn: ({ subjectId, teacherId }: { subjectId: number; teacherId: number }) =>
      schoolApi.academics.assignSubjectTeacher(activeClassId!, subjectId, teacherId),
    onSuccess: async () => {
      setErrorMessage(null)
      setSuccessMessage('Teacher assignment saved.')
      await refreshAcademicData()
    },
    ...mutationOptions,
  })
  const updateElectives = useMutation({
    mutationFn: (subjectIds: number[]) =>
      schoolApi.academics.setStudentElectives(activeStudentId!, subjectIds),
    onSuccess: async () => {
      setErrorMessage(null)
      setSuccessMessage('Student elective selections saved.')
      await refreshAcademicData()
    },
    ...mutationOptions,
  })
  const createExamination = useMutation({
    mutationFn: schoolApi.academics.createExamination,
    onSuccess: async (created) => {
      setErrorMessage(null)
      setSuccessMessage('Examination saved as a draft.')
      setSelectedExaminationId(created.id)
      setExamName('')
      setDraftComponents({})
      await refreshAcademicData()
    },
    ...mutationOptions,
  })
  const scheduleExamination = useMutation({
    mutationFn: schoolApi.academics.scheduleExamination,
    onSuccess: refreshAcademicData,
    ...mutationOptions,
  })
  const saveMarks = useMutation({
    mutationFn: ({ id, marks }: { id: number; marks: AcademicMarkInput[] }) =>
      schoolApi.academics.enterMarks(id, marks),
    onSuccess: async () => {
      setErrorMessage(null)
      setSuccessMessage('Marks saved. You can now publish results after all marks are complete.')
      await refreshAcademicData()
    },
    ...mutationOptions,
  })
  const correctMarks = useMutation({
    mutationFn: ({ id, reason, marks }: {
      id: number
      reason: string
      marks: AcademicMarkInput[]
    }) => schoolApi.academics.correctMarks(id, reason, marks),
    onSuccess: async () => {
      setErrorMessage(null)
      setSuccessMessage('Published marks corrected and results recalculated.')
      setCorrectionReason('')
      await refreshAcademicData()
    },
    ...mutationOptions,
  })
  const publishExamination = useMutation({
    mutationFn: schoolApi.academics.publishExamination,
    onSuccess: async () => {
      setErrorMessage(null)
      setSuccessMessage('Results have been published to the student portal.')
      await refreshAcademicData()
    },
    ...mutationOptions,
  })
  const lockExamination = useMutation({
    mutationFn: schoolApi.academics.lockExamination,
    onSuccess: async () => {
      setErrorMessage(null)
      setSuccessMessage('Results are locked. Further changes require an authorized correction.')
      await refreshAcademicData()
    },
    ...mutationOptions,
  })
  const saveGrading = useMutation({
    mutationFn: (rules: Array<{
      grade: string
      minimum_percentage: number
      maximum_percentage: number
      description: string | null
    }>) => schoolApi.academics.updateGradingScale('DEFAULT', rules),
    onSuccess: async () => {
      setErrorMessage(null)
      setSuccessMessage('Default grading scale updated.')
      await refreshAcademicData()
    },
    ...mutationOptions,
  })

  const setDraftComponent = (
    subjectId: number,
    index: number,
    field: keyof DraftComponent,
    value: string,
  ) => {
    setDraftComponents((current) => {
      const components = current[subjectId] ?? [{
        name: 'Written',
        component_type: 'theory',
        max_marks: '100',
        passing_marks: '40',
      }]
      const next = [...components]
      next[index] = { ...next[index], [field]: value }
      return { ...current, [subjectId]: next }
    })
  }
  const addDraftComponent = (subjectId: number) => {
    setDraftComponents((current) => ({
      ...current,
      [subjectId]: [
        ...(current[subjectId] ?? [{
          name: 'Written',
          component_type: 'theory',
          max_marks: '100',
          passing_marks: '40',
        }]),
        {
          name: '',
          component_type: 'practical',
          max_marks: '0',
          passing_marks: '0',
        },
      ],
    }))
  }
  const updateGradingDraft = (
    index: number,
    field: 'grade' | 'minimum_percentage' | 'maximum_percentage' | 'description',
    value: string,
  ) => {
    if (!currentGradingDraft) return
    setGradingDraft(currentGradingDraft.map((item, itemIndex) =>
      itemIndex === index ? { ...item, [field]: value } : item))
  }
  const removeDraftComponent = (subjectId: number, index: number) => {
    setDraftComponents((current) => ({
      ...current,
      [subjectId]: (current[subjectId] ?? []).filter((_, itemIndex) => itemIndex !== index),
    }))
  }

  const createExam = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (activeClassId === null || offerings.filter((item) => item.is_active).length === 0) {
      setErrorMessage('Configure at least one active class subject before creating an examination.')
      return
    }
    const examSubjects = offerings.filter((item) => item.is_active).map((offering) => {
      const components = draftComponents[offering.subject_id] ?? [{
        name: 'Written',
        component_type: 'theory' as const,
        max_marks: '100',
        passing_marks: '40',
      }]
      const componentInputs = components.map((component) => ({
        name: component.name.trim(),
        component_type: component.component_type,
        max_marks: Number(component.max_marks),
        passing_marks: Number(component.passing_marks),
      }))
      return {
        subject_id: offering.subject_id,
        teacher_id: offering.teacher_id,
        max_marks: componentInputs.reduce((total, component) => total + component.max_marks, 0),
        passing_marks: componentInputs.reduce((total, component) => total + component.passing_marks, 0),
        components: componentInputs,
      }
    })
    createExamination.mutate({
      name: examName.trim(),
      class_id: activeClassId,
      examination_type: examType,
      start_date: examStart,
      end_date: examEnd,
      subjects: examSubjects,
    })
  }

  const collectMarks = (): AcademicMarkInput[] => roster.flatMap((student) =>
    student.subjects.flatMap((subject) => subject.components.flatMap((component) => {
      const key = markKey(student.student_id, component.id)
      const value = markValues[key] ?? {
        status: component.status === 'ABSENT'
          ? 'ABSENT' as const
          : component.status === 'EXEMPTED'
            ? 'EXEMPTED' as const
            : 'PRESENT' as const,
        obtained_marks: component.obtained_marks === null
          ? ''
          : String(component.obtained_marks),
        remarks: component.remarks ?? '',
      }
      if (value.status === 'PRESENT' && value.obtained_marks.trim() === '') return []
      return [{
        student_id: student.student_id,
        component_id: component.id,
        status: value.status,
        obtained_marks: value.status === 'PRESENT' ? Number(value.obtained_marks) : null,
        remarks: value.remarks.trim() || null,
      }]
    })),
  )

  const classQueryError = [
    classesQuery,
    offeringsQuery,
    catalogQuery,
    teachersQuery,
    studentsQuery,
    examinationsQuery,
    rosterQuery,
    resultsQuery,
    electiveQuery,
    gradingQuery,
  ].find((query) => query.isError)

  return (
    <>
      <PageHeader
        title="Academic management"
        description="Configure class subjects, teacher assignments, student electives, examinations, marks, grades, and published results."
      />
      {errorMessage ? (
        <Alert className="mt-4" variant="destructive">
          <AlertTitle>Academic change could not be saved</AlertTitle>
          <AlertDescription>{errorMessage}</AlertDescription>
        </Alert>
      ) : null}
      {successMessage ? (
        <Alert className="mt-4">
          <AlertTitle>Saved</AlertTitle>
          <AlertDescription>{successMessage}</AlertDescription>
        </Alert>
      ) : null}
      {classQueryError ? (
        <ErrorState
          description={toApiError(classQueryError.error).message}
          onRetry={() => void classQueryError.refetch()}
          title="Academic data could not be loaded"
        />
      ) : null}
      {classesQuery.isPending ? <LoadingState label="Loading classes" /> : null}
      {!classesQuery.isPending && classes.length === 0 ? (
        <EmptyState
          description="Create an active class before configuring its curriculum."
          title="No active classes"
        />
      ) : null}
      {classes.length > 0 ? (
        <div className="mt-5 grid gap-5">
          <Card>
            <CardHeader>
              <CardTitle>Class selection</CardTitle>
              <CardDescription>Select the grade, section, and academic year separately.</CardDescription>
            </CardHeader>
            <CardContent>
              <ClassRecordSelector
                classes={classes}
                initialClassId={classes[0]?.id}
                onChange={(_, schoolClass) => {
                    setClassSelectionIncomplete(!schoolClass)
                    setSelectedClassId(schoolClass?.id ?? null)
                    setSelectedExaminationId(null)
                    setSelectedStudentId(null)
                    setDraftComponents({})
                    setExamName('')
                    setMarkValues({})
                  }}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Subject offerings and teachers</CardTitle>
              <CardDescription>Define mandatory and elective subjects independently for each section and year.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[850px] text-left text-sm">
                  <thead className="text-xs uppercase tracking-wide text-slate-500">
                    <tr>
                      <th className="px-3 py-2">Subject</th>
                      <th className="px-3 py-2">Type</th>
                      <th className="px-3 py-2">Stream</th>
                      <th className="px-3 py-2">Teacher</th>
                      <th className="px-3 py-2">Status</th>
                      <th className="px-3 py-2">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {offerings.map((offering) => (
                      <OfferingSettings
                        busy={configureOffering.isPending || assignTeacher.isPending}
                        key={`${offering.class_id}-${offering.subject_id}-${offering.subject_type}-${offering.stream}-${offering.is_active}-${offering.teacher_id}`}
                        offering={offering}
                        teachers={teachers}
                        onAssignTeacher={(teacherId) => assignTeacher.mutate({
                          subjectId: offering.subject_id,
                          teacherId,
                        })}
                        onSave={(value) => configureOffering.mutate({
                          subjectId: offering.subject_id,
                          value,
                        })}
                      />
                    ))}
                    {offerings.length === 0 ? (
                      <tr><td className="px-3 py-5 text-slate-500" colSpan={6}>No subject offerings yet.</td></tr>
                    ) : null}
                  </tbody>
                </table>
              </div>
              <div className="mt-5 grid gap-3 border-t border-slate-100 pt-4 sm:grid-cols-[1fr_180px_180px_auto]">
                <label className="grid gap-1.5 text-sm font-medium" htmlFor="new-class-subject">
                  Add catalog subject
                  <select
                    className="h-10 rounded-lg border border-input bg-white px-3"
                    id="new-class-subject"
                    onChange={(event) => setNewSubjectId(event.target.value)}
                    value={newSubjectId}
                  >
                    <option value="">Select a subject</option>
                    {availableSubjects.map((subject) => (
                      <option key={subject.id} value={subject.id}>{subject.code} · {subject.name}</option>
                    ))}
                  </select>
                </label>
                <label className="grid gap-1.5 text-sm font-medium">
                  Offering type
                  <select
                    className="h-10 rounded-lg border border-input bg-white px-3"
                    onChange={(event) => setNewSubjectType(event.target.value as ClassSubjectOffering['subject_type'])}
                    value={newSubjectType}
                  >
                    <option value="mandatory">Mandatory</option>
                    <option value="elective">Elective</option>
                    <option value="optional">Optional</option>
                  </select>
                </label>
                <label className="grid gap-1.5 text-sm font-medium">
                  Stream
                  <Input onChange={(event) => setNewStream(event.target.value)} value={newStream} />
                </label>
                <div className="flex items-end">
                  <Button
                    disabled={!newSubjectId || configureOffering.isPending || activeClassId === null}
                    onClick={() => {
                      configureOffering.mutate({
                        subjectId: Number(newSubjectId),
                        value: {
                          subject_type: newSubjectType,
                          stream: newStream.trim() || null,
                          is_active: true,
                        },
                      })
                      setNewSubjectId('')
                      setNewStream('')
                    }}
                    type="button"
                  >
                    Add subject
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Student elective selections</CardTitle>
              <CardDescription>Selections are recorded against the student's class and academic year.</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-4">
              <label className="grid max-w-xl gap-1.5 text-sm font-medium">
                Student
                <select
                  className="h-10 rounded-lg border border-input bg-white px-3"
                  onChange={(event) => setSelectedStudentId(Number(event.target.value))}
                  value={activeStudentId ?? ''}
                >
                  <option value="">Select a student</option>
                  {studentList.map((student) => (
                    <option key={student.id} value={student.id}>
                      {student.student_code} · {student.first_name} {student.last_name}
                    </option>
                  ))}
                </select>
              </label>
              {activeStudentId !== null ? (
                <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                  {electiveSubjects
                    .filter((subject) => subject.subject_type === 'elective' || subject.subject_type === 'optional')
                    .map((subject) => (
                      <label className="flex items-start gap-2 rounded-lg border border-slate-200 p-3 text-sm" key={subject.subject_id}>
                        <input
                          checked={chosenElectiveIds.includes(subject.subject_id)}
                          onChange={(event) => {
                            const next = event.target.checked
                              ? [...chosenElectiveIds, subject.subject_id]
                              : chosenElectiveIds.filter((id) => id !== subject.subject_id)
                            updateElectives.mutate(next)
                          }}
                          type="checkbox"
                        />
                        <span>
                          <span className="block font-medium">{subject.name}</span>
                          <span className="text-xs text-slate-500">{subject.subject_type}{subject.stream ? ` · ${subject.stream}` : ''}</span>
                        </span>
                      </label>
                    ))}
                  {electiveSubjects.every((subject) => subject.subject_type === 'mandatory') ? (
                    <p className="text-sm text-slate-500">This class has no active elective or optional subjects.</p>
                  ) : null}
                </div>
              ) : (
                <p className="text-sm text-slate-500">No active students are enrolled in this class.</p>
              )}
              {electiveSubjects.some((subject) => subject.subject_type === 'mandatory') ? (
                <p className="text-xs text-slate-500">Mandatory subjects are included automatically and cannot be unchecked.</p>
              ) : null}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Create examination</CardTitle>
              <CardDescription>Configure each paper with theory, practical, and internal components as needed.</CardDescription>
            </CardHeader>
            <CardContent>
              {offerings.filter((item) => item.is_active).length === 0 ? (
                <p className="text-sm text-slate-500">Add at least one active subject offering before creating an exam.</p>
              ) : (
                <form className="grid gap-4" onSubmit={createExam}>
                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    <label className="grid gap-1.5 text-sm font-medium">
                      Examination name
                      <Input onChange={(event) => setExamName(event.target.value)} required value={examName} />
                    </label>
                    <label className="grid gap-1.5 text-sm font-medium">
                      Type
                      <select className="h-10 rounded-lg border border-input bg-white px-3" onChange={(event) => setExamType(event.target.value)} value={examType}>
                        <option value="unit_test">Unit test</option>
                        <option value="term">Term examination</option>
                        <option value="mid_term">Mid-term</option>
                        <option value="final_exam">Final examination</option>
                      </select>
                    </label>
                    <label className="grid gap-1.5 text-sm font-medium">
                      Start date
                      <Input onChange={(event) => setExamStart(event.target.value)} required type="date" value={examStart} />
                    </label>
                    <label className="grid gap-1.5 text-sm font-medium">
                      End date
                      <Input onChange={(event) => setExamEnd(event.target.value)} required type="date" value={examEnd} />
                    </label>
                  </div>
                  <div className="grid gap-3">
                    {offerings.filter((item) => item.is_active).map((offering) => {
                      const components = draftComponents[offering.subject_id] ?? [{
                        name: 'Written',
                        component_type: 'theory' as const,
                        max_marks: '100',
                        passing_marks: '40',
                      }]
                      return (
                        <div className="rounded-xl border border-slate-200 p-4" key={offering.subject_id}>
                          <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2">
                            <h3 className="font-semibold">{offering.name}</h3>
                            <span className="text-xs text-slate-500">{offering.subject_type}{offering.teacher_name ? ` · ${offering.teacher_name}` : ''}</span>
                          </div>
                          <div className="grid gap-3">
                            {components.map((component, index) => (
                              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-[1fr_1fr_120px_140px_auto]" key={`${offering.subject_id}-${index}`}>
                                <label className="grid gap-1 text-xs font-medium text-slate-600">
                                  Component
                                  <Input
                                    onChange={(event) => setDraftComponent(offering.subject_id, index, 'name', event.target.value)}
                                    required
                                    value={component.name}
                                  />
                                </label>
                                <label className="grid gap-1 text-xs font-medium text-slate-600">
                                  Component type
                                  <select
                                    className="h-10 rounded-lg border border-input bg-white px-3 text-sm"
                                    onChange={(event) => setDraftComponent(offering.subject_id, index, 'component_type', event.target.value)}
                                    value={component.component_type}
                                  >
                                    <option value="theory">Theory</option>
                                    <option value="practical">Practical</option>
                                    <option value="internal">Internal</option>
                                    <option value="combined">Combined</option>
                                  </select>
                                </label>
                                <label className="grid gap-1 text-xs font-medium text-slate-600">
                                  Maximum
                                  <Input
                                    min="0.01"
                                    onChange={(event) => setDraftComponent(offering.subject_id, index, 'max_marks', event.target.value)}
                                    required
                                    step="0.01"
                                    type="number"
                                    value={component.max_marks}
                                  />
                                </label>
                                <label className="grid gap-1 text-xs font-medium text-slate-600">
                                  Passing
                                  <Input
                                    min="0"
                                    onChange={(event) => setDraftComponent(offering.subject_id, index, 'passing_marks', event.target.value)}
                                    required
                                    step="0.01"
                                    type="number"
                                    value={component.passing_marks}
                                  />
                                </label>
                                <Button
                                  disabled={components.length < 2}
                                  onClick={() => removeDraftComponent(offering.subject_id, index)}
                                  size="sm"
                                  type="button"
                                  variant="ghost"
                                >
                                  Remove
                                </Button>
                              </div>
                            ))}
                          </div>
                          <Button className="mt-3" onClick={() => addDraftComponent(offering.subject_id)} size="sm" type="button" variant="outline">
                            Add component
                          </Button>
                        </div>
                      )
                    })}
                  </div>
                  <div className="flex justify-end">
                    <Button disabled={createExamination.isPending || !examStart || !examEnd || !examName.trim()} type="submit">
                      {createExamination.isPending ? 'Creating…' : 'Create draft examination'}
                    </Button>
                  </div>
                </form>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Manage examinations and marks</CardTitle>
              <CardDescription>Marks are checked against each component maximum. Publishing locks normal edits.</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-5">
              <label className="grid max-w-xl gap-1.5 text-sm font-medium">
                Examination
                <select
                  className="h-10 rounded-lg border border-input bg-white px-3"
                  onChange={(event) => {
                    setSelectedExaminationId(Number(event.target.value))
                    setMarkValues({})
                  }}
                  value={activeExaminationId ?? ''}
                >
                  <option value="">Select an examination</option>
                  {examinations.map((examination) => (
                    <option key={examination.id} value={examination.id}>
                      {examination.name} · {examination.status}
                    </option>
                  ))}
                </select>
              </label>
              {selectedExamination ? (
                <>
                  <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg bg-slate-50 p-3">
                    <div>
                      <p className="font-semibold">{selectedExamination.name}</p>
                      <p className="text-sm text-slate-600">
                        {selectedExamination.examination_type} · {selectedExamination.start_date}–{selectedExamination.end_date} · {selectedExamination.status}
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {selectedExamination.status === 'draft' ? (
                        <Button disabled={scheduleExamination.isPending} onClick={() => scheduleExamination.mutate(selectedExamination.id)} type="button">
                          Schedule
                        </Button>
                      ) : null}
                      {selectedExamination.status === 'scheduled' ? (
                        <>
                          <Button
                            disabled={saveMarks.isPending || roster.length === 0}
                            onClick={() => {
                              const marks = collectMarks()
                              if (marks.length === 0) {
                                setErrorMessage('Enter at least one complete mark or absence record first.')
                                return
                              }
                              saveMarks.mutate({ id: selectedExamination.id, marks })
                            }}
                            type="button"
                            variant="outline"
                          >
                            Save marks
                          </Button>
                          <Button disabled={publishExamination.isPending} onClick={() => publishExamination.mutate(selectedExamination.id)} type="button">
                            Publish results
                          </Button>
                        </>
                      ) : null}
                      {selectedExamination.status === 'published' ? (
                        <Button disabled={lockExamination.isPending} onClick={() => lockExamination.mutate(selectedExamination.id)} type="button" variant="outline">
                          Lock results
                        </Button>
                      ) : null}
                    </div>
                  </div>
                  {rosterQuery.isPending ? <LoadingState label="Loading examination roster" /> : null}
                  {roster.length > 0 && (selectedExamination.status === 'scheduled'
                    || selectedExamination.status === 'published'
                    || selectedExamination.status === 'locked') ? (
                    <div className="grid gap-4">
                      {roster.map((student: ExaminationRosterEntry) => (
                        <section className="rounded-xl border border-slate-200 p-4" key={student.student_id}>
                          <div className="mb-3">
                            <h3 className="font-semibold">{student.student_name}</h3>
                            <p className="text-xs text-slate-500">
                              {student.student_code}{student.roll_number ? ` · Roll ${student.roll_number}` : ''}
                            </p>
                          </div>
                          <div className="grid gap-3">
                            {student.subjects.map((subject) => (
                              <div className="rounded-lg bg-slate-50 p-3" key={subject.subject_id}>
                                <h4 className="mb-2 text-sm font-semibold">{subject.subject_name}</h4>
                                <div className="grid gap-2">
                                  {subject.components.map((component) => {
                                    const key = markKey(student.student_id, component.id)
                                    const value = markValues[key] ?? {
                                      status: component.status === 'ABSENT'
                                        ? 'ABSENT' as const
                                        : component.status === 'EXEMPTED'
                                          ? 'EXEMPTED' as const
                                          : 'PRESENT' as const,
                                      obtained_marks: component.obtained_marks === null
                                        ? ''
                                        : String(component.obtained_marks),
                                      remarks: component.remarks ?? '',
                                    }
                                    const readOnly = selectedExamination.status === 'draft'
                                    return (
                                      <div className="grid gap-2 sm:grid-cols-[1fr_150px_150px]" key={component.id}>
                                        <span className="self-center text-sm">
                                          {component.name} <span className="text-xs text-slate-500">(max {component.max_marks})</span>
                                        </span>
                                        <select
                                          aria-label={`${student.student_name} ${component.name} status`}
                                          className="h-9 rounded-lg border border-input bg-white px-2 text-sm"
                                          disabled={readOnly}
                                          onChange={(event) => setMarkValues((current) => ({
                                            ...current,
                                            [key]: { ...value, status: event.target.value as MarkValue['status'] },
                                          }))}
                                          value={value.status}
                                        >
                                          <option value="PRESENT">Present</option>
                                          <option value="ABSENT">Absent</option>
                                          <option value="EXEMPTED">Exempted</option>
                                        </select>
                                        <Input
                                          aria-label={`${student.student_name} ${component.name} marks`}
                                          disabled={readOnly || value.status !== 'PRESENT'}
                                          max={component.max_marks}
                                          min="0"
                                          onChange={(event) => setMarkValues((current) => ({
                                            ...current,
                                            [key]: { ...value, obtained_marks: event.target.value },
                                          }))}
                                          placeholder="Marks"
                                          step="0.01"
                                          type="number"
                                          value={value.obtained_marks}
                                        />
                                      </div>
                                    )
                                  })}
                                </div>
                              </div>
                            ))}
                          </div>
                        </section>
                      ))}
                      {selectedExamination.status === 'published' || selectedExamination.status === 'locked' ? (
                        <div className="grid gap-3 rounded-lg border border-amber-200 bg-amber-50 p-4">
                          <p className="text-sm text-amber-950">Corrections are audited and immediately recalculate published results.</p>
                          <label className="grid gap-1.5 text-sm font-medium">
                            Correction reason
                            <Input onChange={(event) => setCorrectionReason(event.target.value)} value={correctionReason} />
                          </label>
                          <div className="flex justify-end">
                            <Button
                              disabled={correctMarks.isPending || correctionReason.trim().length < 5}
                              onClick={() => {
                                const marks = collectMarks()
                                if (marks.length === 0) {
                                  setErrorMessage('Enter at least one complete mark or absence record first.')
                                  return
                                }
                                correctMarks.mutate({
                                  id: selectedExamination.id,
                                  reason: correctionReason.trim(),
                                  marks,
                                })
                              }}
                              type="button"
                            >
                              Save authorized correction
                            </Button>
                          </div>
                        </div>
                      ) : null}
                    </div>
                  ) : null}
                  {roster.length === 0 && !rosterQuery.isPending ? (
                    <p className="text-sm text-slate-500">No active students are enrolled in this class.</p>
                  ) : null}
                  {selectedExamination.status === 'published' || selectedExamination.status === 'locked' ? (
                    <div className="overflow-x-auto">
                      <h3 className="mb-2 font-semibold">Published result summary</h3>
                      {resultsQuery.isPending ? <LoadingState label="Loading published results" /> : null}
                      <table className="w-full min-w-[560px] text-left text-sm">
                        <thead className="text-xs uppercase tracking-wide text-slate-500">
                          <tr><th className="px-3 py-2">Student</th><th className="px-3 py-2">Marks</th><th className="px-3 py-2">Percentage</th><th className="px-3 py-2">Grade</th><th className="px-3 py-2">Result</th></tr>
                        </thead>
                        <tbody>
                          {(resultsQuery.data ?? []).map((result) => {
                            const student = roster.find((item) => item.student_id === result.student_id)
                            return (
                              <tr className="border-t border-slate-100" key={result.student_id}>
                                <td className="px-3 py-2">{student?.student_name ?? student?.student_code ?? result.student_id}</td>
                                <td className="px-3 py-2">{result.total_obtained_marks} / {result.total_max_marks}</td>
                                <td className="px-3 py-2">{formatPercent(result.percentage)}</td>
                                <td className="px-3 py-2 font-semibold">{result.grade}</td>
                                <td className="px-3 py-2">{result.status}</td>
                              </tr>
                            )
                          })}
                        </tbody>
                      </table>
                    </div>
                  ) : null}
                </>
              ) : (
                <p className="text-sm text-slate-500">Create an examination to enter marks and manage results.</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Default grading scale</CardTitle>
              <CardDescription>The scale is configurable. Ranges must cover 0–100 without gaps or overlaps.</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-3">
              {currentGradingDraft?.map((rule, index) => (
                <div className="grid gap-3 sm:grid-cols-4" key={`${rule.grade}-${index}`}>
                  <label className="grid gap-1 text-xs font-medium text-slate-600">
                    Grade
                    <Input
                      onChange={(event) => updateGradingDraft(index, 'grade', event.target.value)}
                      value={rule.grade}
                    />
                  </label>
                  <label className="grid gap-1 text-xs font-medium text-slate-600">
                    Minimum %
                    <Input
                      min="0"
                      onChange={(event) => updateGradingDraft(index, 'minimum_percentage', event.target.value)}
                      step="0.01"
                      type="number"
                      value={rule.minimum_percentage}
                    />
                  </label>
                  <label className="grid gap-1 text-xs font-medium text-slate-600">
                    Maximum %
                    <Input
                      max="100"
                      onChange={(event) => updateGradingDraft(index, 'maximum_percentage', event.target.value)}
                      min="0"
                      step="0.01"
                      type="number"
                      value={rule.maximum_percentage}
                    />
                  </label>
                  <label className="grid gap-1 text-xs font-medium text-slate-600">
                    Description
                    <Input
                      onChange={(event) => updateGradingDraft(index, 'description', event.target.value)}
                      value={rule.description}
                    />
                  </label>
                </div>
              ))}
              <div className="flex justify-end">
                <Button
                  disabled={!currentGradingDraft || saveGrading.isPending}
                  onClick={() => {
                    if (!currentGradingDraft) return
                    const rules = currentGradingDraft.map((rule) => ({
                      grade: rule.grade,
                      minimum_percentage: Number(rule.minimum_percentage),
                      maximum_percentage: Number(rule.maximum_percentage),
                      description: rule.description.trim() || null,
                    }))
                    saveGrading.mutate(rules)
                  }}
                  type="button"
                  variant="outline"
                >
                  Save grading scale
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : null}
    </>
  )
}
