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
  category: string | null
  description: string | null
  subject_type: 'mandatory' | 'elective' | 'optional'
  max_marks: number | null
  passing_marks: number | null
  is_active: boolean
}

export type ClassSubjectOffering = {
  class_id: number
  class_name: string
  section: string | null
  academic_year: string
  subject_id: number
  code: string
  name: string
  category: string | null
  subject_type: 'mandatory' | 'elective' | 'optional'
  stream: string | null
  is_active: boolean
  teacher_id: number | null
  teacher_name: string | null
}

export type AcademicComponent = {
  id: number
  name: string
  type: 'theory' | 'practical' | 'internal' | 'combined'
  max_marks: number
  passing_marks: number
}

export type AcademicExamSubject = {
  id: number
  subject_id: number
  teacher_id: number | null
  max_marks: number
  passing_marks: number
  components: AcademicComponent[]
}

export type AcademicExamination = {
  id: number
  name: string
  class_id: number
  examination_type: string
  start_date: string
  end_date: string
  status: 'draft' | 'scheduled' | 'published' | 'locked'
  description: string | null
  subjects: AcademicExamSubject[]
}

export type ExaminationComponentInput = {
  name: string
  component_type: 'theory' | 'practical' | 'internal' | 'combined'
  max_marks: number
  passing_marks: number
}

export type ExaminationSubjectInput = {
  subject_id: number
  teacher_id?: number | null
  max_marks: number
  passing_marks: number
  components: ExaminationComponentInput[]
}

export type ExaminationCreate = {
  name: string
  class_id: number
  examination_type: string
  start_date: string
  end_date: string
  description?: string | null
  subjects: ExaminationSubjectInput[]
}

export type AcademicMarkInput = {
  student_id: number
  component_id: number
  status: 'PRESENT' | 'ABSENT' | 'EXEMPTED'
  obtained_marks: number | null
  remarks?: string | null
}

export type ExaminationRosterEntry = {
  student_id: number
  student_code: string
  student_name: string
  roll_number: number | null
  subjects: Array<{
    subject_id: number
    subject_name: string
    components: Array<{
      id: number
      name: string
      max_marks: number
      passing_marks: number
      obtained_marks: number | null
      status: 'PASS' | 'FAIL' | 'ABSENT' | 'EXEMPTED' | null
      remarks: string | null
    }>
  }>
}

export type AcademicResult = {
  student_id: number
  total_max_marks: number
  total_obtained_marks: number
  percentage: number
  grade: string
  status: 'PASS' | 'FAIL'
}

export type StudentAcademicResult = {
  examination_id: number
  examination_name: string
  examination_type: string
  start_date: string
  academic_year: string
  total_max_marks: number
  total_obtained_marks: number
  percentage: number
  grade: string
  status: 'PASS' | 'FAIL'
  marks: Array<{
    subject_id: number
    subject_name: string
    component: string
    max_marks: number
    obtained_marks: number | null
    status: 'PASS' | 'FAIL' | 'ABSENT' | 'EXEMPTED'
  }>
}

export type Student = {
  id: number
  student_code: string
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
    list(params: ListParams, filters: {
      name?: string
      section?: string
      section_is_null?: boolean
      academic_year?: string
      status?: string
    }) {
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
    create(payload: {
      code: string
      name: string
      category?: string | null
      description?: string | null
      subject_type?: Subject['subject_type']
      max_marks?: number | null
      passing_marks?: number | null
    }) {
      return requestData<Subject>({ method: 'POST', url: '/subjects', data: payload })
    },
    update(id: number, payload: {
      code?: string
      name?: string
      category?: string | null
      description?: string | null
      subject_type?: Subject['subject_type']
      max_marks?: number | null
      passing_marks?: number | null
    }) {
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
  academics: {
    classSubjects(classId: number) {
      return requestData<ClassSubjectOffering[]>({
        method: 'GET',
        url: `/academics/classes/${classId}/subjects`,
      })
    },
    configureClassSubject(
      classId: number,
      subjectId: number,
      payload: {
        subject_type: ClassSubjectOffering['subject_type']
        stream?: string | null
        is_active: boolean
      },
    ) {
      return requestData<{ class_id: number; subject_id: number }>({
        method: 'PUT',
        url: `/academics/classes/${classId}/subjects/${subjectId}`,
        data: payload,
      })
    },
    assignSubjectTeacher(classId: number, subjectId: number, teacherId: number) {
      return requestData<{ class_id: number; subject_id: number; teacher_id: number }>({
        method: 'PUT',
        url: `/academics/classes/${classId}/subjects/${subjectId}/teacher`,
        params: { teacher_id: teacherId },
      })
    },
    studentSubjects(studentId: number) {
      return requestData<Array<{
        student_id: number
        subject_id: number
        code: string
        name: string
        subject_type: ClassSubjectOffering['subject_type']
        stream: string | null
        selected: boolean
      }>>({ method: 'GET', url: `/academics/students/${studentId}/subjects` })
    },
    setStudentElectives(studentId: number, subjectIds: number[]) {
      return requestData<unknown>({
        method: 'PUT',
        url: `/academics/students/${studentId}/electives`,
        data: subjectIds,
      })
    },
    examinations(classId?: number) {
      return requestData<AcademicExamination[]>({
        method: 'GET',
        url: '/academics/examinations',
        params: classId ? { class_id: classId } : undefined,
      })
    },
    createExamination(payload: ExaminationCreate) {
      return requestData<AcademicExamination>({
        method: 'POST',
        url: '/academics/examinations',
        data: payload,
      })
    },
    scheduleExamination(id: number) {
      return requestData<AcademicExamination>({
        method: 'POST',
        url: `/academics/examinations/${id}/schedule`,
      })
    },
    enterMarks(id: number, marks: AcademicMarkInput[]) {
      return requestData<{ examination_id: number; saved_count: number }>({
        method: 'POST',
        url: `/academics/examinations/${id}/marks`,
        data: { marks },
      })
    },
    examinationRoster(id: number) {
      return requestData<ExaminationRosterEntry[]>({
        method: 'GET',
        url: `/academics/examinations/${id}/roster`,
      })
    },
    publishExamination(id: number) {
      return requestData<AcademicExamination>({
        method: 'POST',
        url: `/academics/examinations/${id}/publish`,
      })
    },
    lockExamination(id: number) {
      return requestData<AcademicExamination>({
        method: 'POST',
        url: `/academics/examinations/${id}/lock`,
      })
    },
    correctMarks(id: number, reason: string, marks: AcademicMarkInput[]) {
      return requestData<{ examination_id: number; corrected_count: number }>({
        method: 'POST',
        url: `/academics/examinations/${id}/corrections`,
        data: { reason, marks },
      })
    },
    results(id: number) {
      return requestData<AcademicResult[]>({
        method: 'GET',
        url: `/academics/examinations/${id}/results`,
      })
    },
    gradingScale(code: string) {
      return requestData<Array<{
        grade: string
        minimum_percentage: number
        maximum_percentage: number
        description: string | null
      }>>({ method: 'GET', url: `/academics/grading-scales/${code}` })
    },
    updateGradingScale(code: string, rules: Array<{
      grade: string
      minimum_percentage: number
      maximum_percentage: number
      description?: string | null
    }>) {
      return requestData({ method: 'PUT', url: `/academics/grading-scales/${code}`, data: { rules } })
    },
    mySubjects() {
      return requestData<Array<{
        student_id: number
        subject_id: number
        code: string
        name: string
        subject_type: ClassSubjectOffering['subject_type']
        stream: string | null
        selected: boolean
      }>>({ method: 'GET', url: '/academics/students/me/subjects' })
    },
    myResults() {
      return requestData<StudentAcademicResult[]>({
        method: 'GET',
        url: '/academics/students/me/results',
      })
    },
  },
}

export type SchoolApi = typeof schoolApi
export type SchoolListQuery<T> = (
  params: ListParams,
  filters: Record<string, unknown>,
) => Promise<PaginatedData<T>>
