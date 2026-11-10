import { requestData } from '@/lib/api/api-client'

export type StudentPortalProfile = {
  student_id: string
  admission_id: string
  first_name: string
  middle_name: string | null
  last_name: string
  father_name: string | null
  mother_name: string | null
  date_of_birth: string
  gender: string
  class_name: string | null
  section: string | null
  academic_year: string | null
  email: string
  phone: string | null
  address: string | null
  admission_date: string | null
  student_photo_url: string | null
  status: string
}

export type AdmissionFeeStructure = {
  structure_name: string
  total_amount: string | number
  components: Array<{
    id: number
    fee_name: string
    amount: string | number
    is_optional: boolean
    is_refundable: boolean
  }>
}

export type MonthlyFeeStructure = {
  structure_name: string
  mandatory_annual_total: string | number
  optional_annual_total: string | number
  total_annual_amount: string | number
  components: Array<{
    id: number
    fee_name: string
    amount: string | number
    billing_frequency: 'MONTHLY' | 'QUARTERLY' | 'ANNUALLY' | 'ONE_TIME'
    is_optional: boolean
  }>
}

export type StudentPortalFees = {
  student_id: string
  class_id: number | null
  academic_year: string | null
  admission_fee_structure: AdmissionFeeStructure | null
  monthly_fee_structure: MonthlyFeeStructure | null
  payment_records_available: boolean
  paid_amount: string | number | null
  pending_amount: string | number | null
  upcoming_due_date: string | null
  payment_status: 'PAID' | 'PARTIALLY_PAID' | 'PENDING' | 'OVERDUE' | null
  billing_message: string
}

export const studentPortalApi = {
  profile() {
    return requestData<StudentPortalProfile>({ method: 'GET', url: '/students/me' })
  },
  fees() {
    return requestData<StudentPortalFees>({ method: 'GET', url: '/students/me/fees' })
  },
}
