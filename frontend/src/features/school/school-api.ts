import { requestData } from '@/lib/api/api-client'
import { requestPaginated } from '@/lib/api/pagination'
import type { PaginatedData } from '@/lib/api/pagination'

export type ListParams = {
  page: number
  limit: number
  sort_by: string
  sort_order: 'asc' | 'desc'
}

export type Teacher = {
  id: number
  employee_no: string
  first_name: string
  last_name: string
  email: string
  phone: string | null
  joining_date: string | null
  status: 'active' | 'inactive' | 'resigned'
}

export type TeacherCreate = {
  employee_no: string
  first_name: string
  last_name: string
  email: string
  phone: string
  joining_date: string
}

export type TeacherUpdate = Partial<Pick<
  Teacher,
  'first_name' | 'last_name' | 'email' | 'phone' | 'status'
>>

export type SchoolClass = {
  id: number
  class_teacher_id: number | null
  name: string
  section: string | null
  academic_year: string
  capacity: number
  status: 'active' | 'inactive'
}

export type ClassCreate = {
  name: string
  section?: string | null
  academic_year: string
  capacity: number
}

export type ClassUpdate = Partial<ClassCreate & Pick<SchoolClass, 'status'>>

export type Subject = {
  id: number
  code: string
  name: string
  is_active: boolean
}

export type Student = {
  id: number
  admission_no: string | null
  first_name: string
  last_name: string
  date_of_birth: string
  gender: string
  email: string | null
  phone: string | null
  current_class_id: number | null
  status: 'prospective' | 'active' | 'inactive' | 'graduated' | 'transferred'
}

export type StudentCreate = {
  admission_no?: string | null
  first_name: string
  last_name: string
  date_of_birth: string
  gender: string
  email?: string | null
  phone?: string | null
  current_class_id?: number | null
}

export type StudentUpdate = Partial<Omit<StudentCreate, 'admission_no' | 'current_class_id'>>

export type ClassReadiness = {
  class_id: number
  ready: boolean
  class_teacher_id: number | null
  active_subject_ids: number[]
  issues: string[]
}

export type TeacherClassSubject = {
  class_id: number
  subject_id: number
  class_name: string
  subject_name: string
}

export type ClassSubject = Subject

const listParams = (params: ListParams) => ({
  ...params,
  sort_by: params.sort_by,
  sort_order: params.sort_order,
})

export const schoolApi = {
  teachers: {
    list(params: ListParams, filters: { search?: string; status?: string }) {
      return requestPaginated<Teacher>({
        method: 'GET',
        url: '/teachers',
        params: { ...listParams(params), ...filters },
      })
    },
    get(id: number) {
      return requestData<Teacher>({ method: 'GET', url: `/teachers/${id}` })
    },
    create(payload: TeacherCreate) {
      return requestData<Teacher>({ method: 'POST', url: '/teachers', data: payload })
    },
    update(id: number, payload: TeacherUpdate) {
      return requestData<Teacher>({ method: 'PUT', url: `/teachers/${id}`, data: payload })
    },
    classSubjects(id: number) {
      return requestData<TeacherClassSubject[]>({
        method: 'GET',
        url: `/teachers/${id}/class-subjects`,
      })
    },
    assignClassSubject(id: number, classId: number, subjectId: number) {
      return requestData<{ teacher_id: number; class_id: number; subject_id: number }>({
        method: 'POST',
        url: `/teachers/${id}/class-subjects`,
        data: { class_id: classId, subject_id: subjectId },
      })
    },
    removeClassSubject(id: number, classId: number, subjectId: number) {
      return requestData<null>({
        method: 'DELETE',
        url: `/teachers/${id}/class-subjects/${classId}/${subjectId}`,
      })
    },
  },
  classes: {
    list(params: ListParams, filters: { academic_year?: string; status?: string }) {
      return requestPaginated<SchoolClass>({
        method: 'GET',
        url: '/classes/',
        params: { ...listParams(params), ...filters },
      })
    },
    get(id: number) {
      return requestData<SchoolClass>({ method: 'GET', url: `/classes/${id}` })
    },
    create(payload: ClassCreate) {
      return requestData<SchoolClass>({ method: 'POST', url: '/classes/', data: payload })
    },
    update(id: number, payload: ClassUpdate) {
      return requestData<SchoolClass>({ method: 'PUT', url: `/classes/${id}`, data: payload })
    },
    delete(id: number) {
      return requestData<null>({ method: 'DELETE', url: `/classes/${id}` })
    },
    readiness(id: number) {
      return requestData<ClassReadiness>({
        method: 'GET',
        url: `/classes/${id}/readiness`,
      })
    },
    subjects(id: number) {
      return requestData<ClassSubject[]>({ method: 'GET', url: `/classes/${id}/subjects` })
    },
    assignSubject(classId: number, subjectId: number) {
      return requestData<{ class_id: number; subject_id: number }>({
        method: 'POST',
        url: `/classes/${classId}/subjects`,
        data: { subject_id: subjectId },
      })
    },
    removeSubject(classId: number, subjectId: number) {
      return requestData<null>({
        method: 'DELETE',
        url: `/classes/${classId}/subjects/${subjectId}`,
      })
    },
    assignTeacher(classId: number, teacherId: number, replace: boolean) {
      return requestData<{ class_id: number; teacher_id: number }>({
        method: replace ? 'PUT' : 'POST',
        url: `/classes/${classId}/class-teacher`,
        data: { teacher_id: teacherId },
      })
    },
    removeTeacher(classId: number) {
      return requestData<null>({ method: 'DELETE', url: `/classes/${classId}/class-teacher` })
    },
  },
  subjects: {
    list(params: ListParams, filters: { search?: string; active?: boolean }) {
      return requestPaginated<Subject>({
        method: 'GET',
        url: '/subjects',
        params: { ...listParams(params), ...filters },
      })
    },
    get(id: number) {
      return requestData<Subject>({ method: 'GET', url: `/subjects/${id}` })
    },
    create(payload: { code: string; name: string }) {
      return requestData<Subject>({ method: 'POST', url: '/subjects', data: payload })
    },
    update(id: number, payload: { code: string; name: string }) {
      return requestData<Subject>({ method: 'PUT', url: `/subjects/${id}`, data: payload })
    },
    deactivate(id: number) {
      return requestData<Subject>({ method: 'DELETE', url: `/subjects/${id}` })
    },
    activate(id: number) {
      return requestData<Subject>({ method: 'POST', url: `/subjects/${id}/activate` })
    },
  },
  students: {
    list(params: ListParams, filters: {
      search?: string
      status?: string
      current_class_id?: number
    }) {
      return requestPaginated<Student>({
        method: 'GET',
        url: '/students',
        params: { ...listParams(params), ...filters },
      })
    },
    get(id: number) {
      return requestData<Student>({ method: 'GET', url: `/students/${id}` })
    },
    create(payload: StudentCreate) {
      return requestData<Student>({ method: 'POST', url: '/students', data: payload })
    },
    update(id: number, payload: StudentUpdate) {
      return requestData<Student>({ method: 'PUT', url: `/students/${id}`, data: payload })
    },
    updateStatus(id: number, status: Student['status'], reason?: string) {
      return requestData<Student>({
        method: 'PUT',
        url: `/students/${id}/status`,
        data: { status, reason: reason || null },
      })
    },
    assignClass(id: number, classId: number, academicYear: string) {
      return requestData<Student>({
        method: 'PUT',
        url: `/students/${id}/class`,
        data: { class_id: classId, academic_year: academicYear },
      })
    },
    delete(id: number) {
      return requestData<null>({ method: 'DELETE', url: `/students/${id}` })
    },
    listSubjects(id: number) {
      return requestData<Subject[]>({ method: 'GET', url: `/students/${id}/subjects` })
    },
  },
}

export type SchoolApi = typeof schoolApi
export type SchoolListQuery<T> = (
  params: ListParams,
  filters: Record<string, unknown>,
) => Promise<PaginatedData<T>>
