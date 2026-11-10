import {
  requestBlob,
  requestData,
  requestPublicBlob,
  requestPublicData,
} from '@/lib/api/api-client'
import { requestPaginated } from '@/lib/api/pagination'
import type { ListParams } from '@/features/school/school-api'

export type InquiryStatus =
  | 'PENDING'
  | 'UNDER_REVIEW'
  | 'PROCESSING'
  | 'INTERVIEW_SCHEDULED'
  | 'INTERVIEW_PASS'
  | 'INTERVIEW_FAIL'
  | 'DOCUMENT_PENDING'
  | 'DOCUMENT_VERIFICATION'
  | 'ADMISSION_SUCCESS'
  | 'REJECTED'

export type InquiryHistory = {
  id: number
  from_status: string | null
  to_status: string
  change_reason: string | null
  created_at: string
}

export type Interview = {
  id: number
  inquiry_id: number
  schedule_date: string
  schedule_time: string
  location: string
  mode: 'ONLINE' | 'OFFLINE'
  interviewer_teacher_id: number | null
  remarks: string | null
  result: 'SCHEDULED' | 'PASSED' | 'FAILED' | 'ABSENT'
}

export type Inquiry = {
  id: number
  inquiry_code: string
  serial_number: number
  first_name: string
  middle_name: string | null
  last_name: string
  gender: 'male' | 'female' | 'other'
  father_name: string
  date_of_birth: string
  student_mobile: string | null
  parent_mobile: string
  email: string
  address: string
  last_school: string
  current_class: string
  admission_for_class: string
  last_school_percentage: number | null
  admission_for_class_id: number | null
  status: InquiryStatus
  rejection_reason: string | null
  internal_notes: string | null
  created_at: string
  updated_at: string | null
  status_timeline: InquiryHistory[]
  interviews?: Interview[]
}

export type InquiryCreate = {
  first_name: string
  middle_name?: string | null
  last_name: string
  gender: 'male' | 'female' | 'other'
  father_name: string
  dob: string
  student_mobile?: string | null
  parent_mobile: string
  email: string
  address: string
  last_school: string
  current_class: string
  admission_for_class: string
  last_school_percentage?: number | null
  admission_for_class_id?: number | null
}

export type InquiryCreated = {
  inquiry_code: string
  status: InquiryStatus
  message: string
}

export type PublicInquiryStatus = {
  inquiry_code: string
  status: string
  rejection_reason: string | null
  admission_for_class: string
  created_at: string
  updated_at: string | null
  status_timeline: {
    id: number
    from_status: string | null
    to_status: string
    change_reason: string | null
    created_at: string
  }[]
  latest_interview: {
    schedule_date: string
    schedule_time: string
    location: string
    mode: string
    result: string
  } | null
  admission: {
    admission_code: string | null
    status: string | null
    documents_uploaded: number
    documents_required: number
    documents?: {
      document_type: DocumentType
      verification_status: 'PENDING' | 'VERIFIED' | 'REJECTED'
      rejection_reason: string | null
    }[]
    student_code?: string | null
    student_name?: string | null
    class_name?: string | null
    section?: string | null
    academic_year?: string | null
    roll_number?: number | null
  } | null
}

export type DocumentType =
  | 'progress_report'
  | 'transfer_certificate'
  | 'migration_certificate'
  | 'character_certificate'
  | 'student_aadhar'
  | 'parent_aadhar'

export type PublicAdmissionClass = {
  id: number
  name: string
  section: string | null
  academic_year: string
}

export type PublicAdmissionCreated = {
  admission_code: string
  status: string
}

export type AdmissionDocument = {
  id: number
  admission_id: number
  document_type: string
  file_name: string
  verification_status: 'PENDING' | 'VERIFIED' | 'REJECTED'
  rejection_reason: string | null
  verified_at: string | null
}

export type Admission = {
  id: number
  admission_code: string
  inquiry_id: number
  class_id: number
  class_name?: string | null
  section: string | null
  academic_year: string
  status: 'draft' | 'submitted' | 'document_pending' | 'document_verification' | 'approved' | 'rejected'
  permanent_address: string | null
  student_aadhaar_masked?: string | null
  parent_aadhaar_masked?: string | null
  last_school_marks?: number | null
  last_school_percentage?: number | null
  last_school_id_or_roll_number?: string | null
  temporary_address: string | null
  nationality: string | null
  disability: string | null
  blood_group: string | null
  reason_for_school_change: string | null
  rejection_reason: string | null
  notes: string | null
  student_id: number | null
  documents: AdmissionDocument[]
}

export type EnrollmentResult = {
  student_id: number
  student_code: string
  admission_id: number
  admission_code: string
  inquiry_code: string
  class_id: number
  section: string | null
  academic_year: string
  roll_number: number
}

export type AdmissionCreate = {
  class_id: number
  section?: string | null
  academic_year: string
  permanent_address?: string | null
  temporary_address?: string | null
  nationality?: string | null
  disability?: string | null
  blood_group?: string | null
  reason_for_school_change?: string | null
  notes?: string | null
}

export type AdmissionUpdate = Partial<AdmissionCreate>

export const admissionsApi = {
  public: {
    listAdmissionClasses() {
      return requestPublicData<PublicAdmissionClass[]>({
        method: 'GET',
        url: '/public/student/classes',
      })
    },
    createInquiry(payload: InquiryCreate) {
      return requestPublicData<InquiryCreated>({
        method: 'POST',
        url: '/public/student/inquiry',
        data: payload,
      })
    },
    getInquiryStatus(inquiryCode: string, email: string, parentMobile: string) {
      return requestPublicData<PublicInquiryStatus>({
        method: 'GET',
        url: `/public/student/inquiry/status/${encodeURIComponent(inquiryCode.trim())}`,
        headers: {
          'X-Parent-Email': email,
          'X-Parent-Mobile': parentMobile,
        },
      })
    },
    updateInquiry(payload: {
      inquiry_code: string
      email: string
      parent_mobile: string
      first_name?: string
      middle_name?: string | null
      last_name?: string
      gender?: 'male' | 'female' | 'other'
      father_name?: string
      dob?: string
      student_mobile?: string | null
      address?: string
      last_school?: string
      current_class?: string
      admission_for_class?: string
      last_school_percentage?: number | null
    }) {
      return requestPublicData<PublicInquiryStatus>({
        method: 'PUT',
        url: '/public/student/inquiry/update',
        data: payload,
      })
    },
    submitAdmission(payload: {
      inquiry_code: string
      email: string
      parent_mobile: string
      class_id: number
      academic_year: string
      section?: string
      permanent_address?: string
      student_aadhaar: string
      parent_aadhaar: string
      last_school_marks: number
      last_school_percentage: number
      last_school_id_or_roll_number: string
    }) {
      const body = new FormData()
      body.set('inquiry_code', payload.inquiry_code)
      body.set('email', payload.email)
      body.set('parent_mobile', payload.parent_mobile)
      body.set('class_id', String(payload.class_id))
      body.set('academic_year', payload.academic_year)
      if (payload.section) body.set('section', payload.section)
      if (payload.permanent_address) body.set('permanent_address', payload.permanent_address)
      body.set('student_aadhaar', payload.student_aadhaar)
      body.set('parent_aadhaar', payload.parent_aadhaar)
      body.set('last_school_marks', String(payload.last_school_marks))
      body.set('last_school_percentage', String(payload.last_school_percentage))
      body.set('last_school_id_or_roll_number', payload.last_school_id_or_roll_number)

      return requestPublicData<PublicAdmissionCreated>({
        method: 'POST',
        url: '/public/student/admission',
        data: body,
      })
    },
    uploadAdmissionDocument(
      credentials: { inquiry_code: string; email: string; parent_mobile: string },
      documentType: DocumentType,
      file: File,
    ) {
      const body = new FormData()
      body.set('inquiry_code', credentials.inquiry_code)
      body.set('email', credentials.email)
      body.set('parent_mobile', credentials.parent_mobile)
      body.set('document_type', documentType)
      body.set('file', file)
      return requestPublicData<{
        document_type: DocumentType
        verification_status: 'PENDING' | 'VERIFIED' | 'REJECTED'
        rejection_reason: string | null
        verified_at: string | null
      }>({
        method: 'POST',
        url: '/public/student/admission/documents',
        data: body,
      })
    },
    downloadAdmissionLetter(
      inquiryCode: string,
      email: string,
      parentMobile: string,
    ) {
      return requestPublicBlob({
        method: 'GET',
        url: `/public/student/inquiry/status/${encodeURIComponent(inquiryCode)}/admission-letter`,
        headers: {
          'X-Parent-Email': email,
          'X-Parent-Mobile': parentMobile,
        },
      })
    },
  },
  inquiries: {
    list(
      params: ListParams,
      filters: { status?: InquiryStatus; admission_for_class_id?: number; search?: string },
    ) {
      return requestPaginated<Inquiry>({
        method: 'GET',
        url: '/inquiries',
        params: { ...params, ...filters },
      })
    },
    get(id: number) {
      return requestData<Inquiry>({ method: 'GET', url: `/inquiries/${id}` })
    },
    create(payload: InquiryCreate) {
      return admissionsApi.public.createInquiry(payload)
    },
    updateStaff(id: number, payload: { admission_for_class_id?: number; internal_notes?: string }) {
      return requestData<Inquiry>({
        method: 'PUT',
        url: `/inquiries/${id}`,
        data: payload,
      })
    },
    startReview(id: number, notes?: string) {
      return requestData<Inquiry>({
        method: 'POST',
        url: `/inquiries/${id}/review/start`,
        data: notes ? { notes } : {},
      })
    },
    markProcessing(id: number, notes?: string) {
      return requestData<Inquiry>({
        method: 'POST',
        url: `/inquiries/${id}/review/process`,
        data: notes ? { notes } : {},
      })
    },
    reject(id: number, rejection_reason: string) {
      return requestData<Inquiry>({
        method: 'POST',
        url: `/inquiries/${id}/reject`,
        data: { rejection_reason },
      })
    },
  },
  interviews: {
    listForInquiry(inquiryId: number) {
      return requestData<Interview[]>({
        method: 'GET',
        url: `/interviews/inquiries/${inquiryId}`,
      })
    },
    get(id: number) {
      return requestData<Interview>({ method: 'GET', url: `/interviews/${id}` })
    },
    schedule(
      inquiryId: number,
      payload: {
        schedule_date: string
        schedule_time: string
        location: string
        mode: 'ONLINE' | 'OFFLINE'
        interviewer_teacher_id?: number
        remarks?: string
      },
    ) {
      return requestData<Interview>({
        method: 'POST',
        url: `/interviews/inquiries/${inquiryId}/schedule`,
        data: payload,
      })
    },
    recordResult(id: number, result: 'PASSED' | 'FAILED' | 'ABSENT', remarks?: string) {
      return requestData<Interview>({
        method: 'POST',
        url: `/interviews/${id}/result`,
        data: { result, remarks },
      })
    },
  },
  admissions: {
    list(
      params: ListParams,
      filters: { status?: Admission['status']; academic_year?: string },
    ) {
      return requestPaginated<Admission>({
        method: 'GET',
        url: '/inquiry-admissions',
        params: { ...params, ...filters },
      })
    },
    get(id: number) {
      return requestData<Admission>({ method: 'GET', url: `/inquiry-admissions/${id}` })
    },
    createFromInquiry(inquiryId: number, payload: AdmissionCreate) {
      return requestData<Admission>({
        method: 'POST',
        url: `/inquiries/${inquiryId}/admission`,
        data: payload,
      })
    },
    update(id: number, payload: AdmissionUpdate) {
      return requestData<Admission>({
        method: 'PUT',
        url: `/inquiry-admissions/${id}`,
        data: payload,
      })
    },
    approve(id: number) {
      return requestData<Admission>({
        method: 'POST',
        url: `/inquiry-admissions/${id}/approve`,
      })
    },
    reject(id: number, rejection_reason: string) {
      return requestData<Admission>({
        method: 'POST',
        url: `/inquiry-admissions/${id}/reject`,
        data: { rejection_reason },
      })
    },
    enroll(id: number) {
      return requestData<EnrollmentResult>({
        method: 'POST',
        url: `/inquiry-admissions/${id}/enroll`,
      })
    },
    requiredDocuments() {
      return requestData<{ required: DocumentType[] }>({
        method: 'GET',
        url: '/documents/required',
      })
    },
    viewDocument(id: number) {
      return requestBlob({
        method: 'GET',
        url: `/documents/${id}/file`,
      })
    },
    verifyDocument(id: number, verified: boolean, rejection_reason?: string) {
      return requestData<AdmissionDocument>({
        method: 'POST',
        url: `/documents/${id}/verify`,
        params: { verified },
        data: verified ? undefined : { rejection_reason },
      })
    },
  },
}
