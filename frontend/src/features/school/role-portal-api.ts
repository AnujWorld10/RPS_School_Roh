import { apiClient, requestData, requestPublicData } from '@/lib/api/api-client'
import { toApiError } from '@/lib/api/api-error'

export type TeachingAssignment = {
  class_id: number
  subject_id: number
  class_name: string
  subject_name: string
}

export type AssignmentAttachment = {
  id: number
  file_name: string
  content_type: string | null
  created_at: string
}

export type SchoolAssignment = {
  id: number
  title: string
  details: string
  class_id: number
  subject_id: number
  assigned_teacher_id: number
  assigned_date: string
  due_date: string
  status: 'draft' | 'published' | 'closed'
  attachments: AssignmentAttachment[]
}

export type TimetableEntry = {
  id: number
  class_id: number
  subject_id: number
  teacher_id: number
  day_of_week: number
  start_time: string
  end_time: string
  room: string | null
  academic_year: string
}

export type AssessmentResult = {
  id: number
  assessment_id: number
  student_id: number
  score: string | number | null
  result_status: 'present' | 'absent'
  remarks: string | null
}

export type SchoolAssessment = {
  id: number
  name: string
  assessment_type: string
  class_id: number
  subject_id: number
  teacher_id: number
  assessment_date: string
  max_score: string | number
  is_published: boolean
  results: AssessmentResult[]
}

export type SchoolEvent = {
  id: number
  title: string
  description: string
  starts_at: string
  ends_at: string
  venue: string | null
  audience: 'public' | 'students' | 'parents' | 'all'
  status: 'pending_review' | 'published' | 'rejected'
  created_by: number
  reviewed_by: number | null
  rejection_reason: string | null
}

export type AssignmentCreate = {
  title: string
  details: string
  class_id: number
  subject_id: number
  due_date: string
}

export type AssessmentCreate = {
  name: string
  assessment_type:
    | 'unit_test'
    | 'periodic_test'
    | 'mid_term'
    | 'final_exam'
    | 'assignment'
    | 'quiz'
    | 'practical'
    | 'oral'
  class_id: number
  subject_id: number
  assessment_date: string
  max_score: number
}

export type TimetableCreate = {
  class_id: number
  subject_id: number
  day_of_week: number
  start_time: string
  end_time: string
  room?: string
  academic_year: string
}

export type EventCreate = {
  title: string
  description: string
  starts_at: string
  ends_at: string
  venue?: string
  audience: 'public' | 'students' | 'parents' | 'all'
}

export const rolePortalApi = {
  teachingAssignments: {
    list() {
      return requestData<TeachingAssignment[]>({
        method: 'GET',
        url: '/teachers/me/class-subjects',
      })
    },
    add(classId: number, subjectId: number) {
      return requestData<{ class_id: number; subject_id: number }>({
        method: 'POST',
        url: '/teachers/me/class-subjects',
        params: { class_id: classId, subject_id: subjectId },
      })
    },
    remove(classId: number, subjectId: number) {
      return requestData<null>({
        method: 'DELETE',
        url: `/teachers/me/class-subjects/${classId}/${subjectId}`,
      })
    },
  },
  assignments: {
    list() {
      return requestData<SchoolAssignment[]>({ method: 'GET', url: '/assignments' })
    },
    create(payload: AssignmentCreate) {
      return requestData<SchoolAssignment>({
        method: 'POST',
        url: '/assignments',
        data: payload,
      })
    },
    publish(id: number) {
      return requestData<SchoolAssignment>({
        method: 'POST',
        url: `/assignments/${id}/publish`,
      })
    },
    uploadAttachment(id: number, file: File) {
      const data = new FormData()
      data.append('file', file)
      return requestData<AssignmentAttachment>({
        method: 'POST',
        url: `/assignments/${id}/attachments`,
        data,
      })
    },
    async downloadAttachment(assignmentId: number, attachmentId: number) {
      try {
        const response = await apiClient.get<Blob>(
          `/assignments/${assignmentId}/attachments/${attachmentId}`,
          { responseType: 'blob' },
        )
        return response.data
      } catch (error) {
        throw toApiError(error)
      }
    },
  },
  timetable: {
    list() {
      return requestData<TimetableEntry[]>({ method: 'GET', url: '/timetable' })
    },
    create(payload: TimetableCreate) {
      return requestData<TimetableEntry>({
        method: 'POST',
        url: '/timetable',
        data: payload,
      })
    },
  },
  assessments: {
    list() {
      return requestData<SchoolAssessment[]>({ method: 'GET', url: '/assessments' })
    },
    create(payload: AssessmentCreate) {
      return requestData<SchoolAssessment>({
        method: 'POST',
        url: '/assessments',
        data: payload,
      })
    },
    saveResult(
      assessmentId: number,
      studentId: number,
      payload: { score: number | null; result_status: 'present' | 'absent'; remarks?: string },
    ) {
      return requestData<AssessmentResult>({
        method: 'PUT',
        url: `/assessments/${assessmentId}/results/${studentId}`,
        data: payload,
      })
    },
    publish(id: number) {
      return requestData<SchoolAssessment>({
        method: 'POST',
        url: `/assessments/${id}/publish`,
      })
    },
  },
  events: {
    list() {
      return requestData<SchoolEvent[]>({ method: 'GET', url: '/events' })
    },
    create(payload: EventCreate) {
      return requestData<SchoolEvent>({ method: 'POST', url: '/events', data: payload })
    },
    review(id: number, status: 'published' | 'rejected', rejectionReason?: string) {
      return requestData<SchoolEvent>({
        method: 'POST',
        url: `/events/${id}/review`,
        data: {
          status,
          rejection_reason: rejectionReason,
        },
      })
    },
  },
  publicEvents() {
    return requestPublicData<SchoolEvent[]>({ method: 'GET', url: '/public/events' })
  },
}
