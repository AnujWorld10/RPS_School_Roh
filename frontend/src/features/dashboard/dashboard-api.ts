import { requestData } from '@/lib/api/api-client'

export type DashboardAdmissionStatus =
  | 'draft'
  | 'submitted'
  | 'document_pending'
  | 'document_verification'
  | 'approved'
  | 'rejected'

export type UpcomingInterviewSummary = {
  id: number
  inquiry_code: string
  student_name: string
  schedule_date: string
  schedule_time: string
  location: string
  mode: 'ONLINE' | 'OFFLINE'
}

export type DashboardSummary = {
  school_timezone: string
  student_count: number | null
  teacher_count: number | null
  class_count: number | null
  subject_count: number | null
  inquiry_count: number | null
  pending_admission_count: number | null
  admissions_by_status: Record<DashboardAdmissionStatus, number> | null
  upcoming_interview_count: number | null
  upcoming_interviews: UpcomingInterviewSummary[] | null
}

export const dashboardApi = {
  summary() {
    return requestData<DashboardSummary>({
      method: 'GET',
      url: '/dashboard/summary',
    })
  },
}
