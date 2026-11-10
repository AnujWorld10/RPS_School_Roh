import { useQuery } from '@tanstack/react-query'
import { CalendarDays, Download, UserRound } from 'lucide-react'
import { useState } from 'react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/async-state'
import { Input } from '@/components/ui/input'
import { PageHeader } from '@/components/ui/page-header'
import { studentPortalApi, type AdmissionFeeStructure, type MonthlyFeeStructure } from '@/features/school/student-portal-api'
import { toApiError } from '@/lib/api/api-error'

const profileQueryKey = ['student-portal', 'profile']
const feesQueryKey = ['student-portal', 'fees']

function formatAmount(value: string | number) {
  const amount = Number(value)
  return Number.isFinite(amount)
    ? new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(amount)
    : 'Not available'
}

function formatDate(value: string | null) {
  if (!value) return 'Not recorded'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? 'Not recorded' : date.toLocaleDateString('en-IN')
}

function ProfileField({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div className="min-w-0 border-b border-slate-100 py-2 last:border-0">
      <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</dt>
      <dd className="mt-1 break-words text-sm font-medium text-slate-900">{value || 'Not on record'}</dd>
    </div>
  )
}

function AdmissionFeeCard({ structure }: { structure: AdmissionFeeStructure }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Admission fee schedule</CardTitle>
        <CardDescription>{structure.structure_name}</CardDescription>
      </CardHeader>
      <CardContent>
        <ul className="divide-y divide-slate-100">
          {structure.components.map((component) => (
            <li className="flex items-start justify-between gap-4 py-3" key={component.id}>
              <span className="text-sm text-slate-700">
                {component.fee_name}
                {component.is_optional ? <span className="ml-1 text-xs text-slate-500">(optional)</span> : null}
              </span>
              <span className="shrink-0 text-sm font-semibold text-slate-900">
                {formatAmount(component.amount)}
              </span>
            </li>
          ))}
        </ul>
        <div className="mt-3 flex justify-between border-t border-slate-200 pt-3 text-sm font-semibold">
          <span>Listed admission charges</span>
          <span>{formatAmount(structure.total_amount)}</span>
        </div>
      </CardContent>
    </Card>
  )
}

function MonthlyFeeCard({ structure }: { structure: MonthlyFeeStructure }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Regular fee schedule</CardTitle>
        <CardDescription>
          {structure.structure_name} · annual schedule amounts, not payment balances
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ul className="divide-y divide-slate-100">
          {structure.components.map((component) => (
            <li className="flex items-start justify-between gap-4 py-3" key={component.id}>
              <span className="text-sm text-slate-700">
                {component.fee_name}
                <span className="ml-1 text-xs text-slate-500">
                  ({component.billing_frequency.toLowerCase().replace('_', ' ')})
                </span>
                {component.is_optional ? <span className="ml-1 text-xs text-slate-500">(optional)</span> : null}
              </span>
              <span className="shrink-0 text-sm font-semibold text-slate-900">
                {formatAmount(component.amount)}
              </span>
            </li>
          ))}
        </ul>
        <div className="mt-3 flex justify-between border-t border-slate-200 pt-3 text-sm font-semibold">
          <span>Annual scheduled total</span>
          <span>{formatAmount(structure.total_annual_amount)}</span>
        </div>
      </CardContent>
    </Card>
  )
}

export function StudentPortalPage() {
  const [selectedMonth, setSelectedMonth] = useState(() => new Date().toISOString().slice(0, 7))
  const profile = useQuery({ queryKey: profileQueryKey, queryFn: studentPortalApi.profile })
  const fees = useQuery({
    queryKey: feesQueryKey,
    queryFn: studentPortalApi.fees,
    enabled: profile.isSuccess,
  })

  return (
    <>
      <PageHeader
        title="Student dashboard"
        description="Your student profile and the fee schedules assigned to your current class."
      />

      {profile.isPending ? <LoadingState label="Loading your student profile" /> : null}
      {profile.isError ? (
        <ErrorState
          description={toApiError(profile.error).message}
          onRetry={() => void profile.refetch()}
          title="Student profile unavailable"
        />
      ) : null}

      {profile.data ? (
        <div className="grid gap-5">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <span className="flex size-11 shrink-0 items-center justify-center rounded-full bg-teal-50 text-teal-900">
                  {profile.data.student_photo_url
                    ? <img alt="" className="size-11 rounded-full object-cover" src={profile.data.student_photo_url} />
                    : <UserRound aria-hidden="true" size={22} />}
                </span>
                <div>
                  <CardTitle>Student profile</CardTitle>
                  <CardDescription>
                    {profile.data.first_name} {profile.data.middle_name ? `${profile.data.middle_name} ` : ''}
                    {profile.data.last_name}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <dl className="grid gap-x-6 sm:grid-cols-2 lg:grid-cols-3">
                <ProfileField label="Student ID" value={profile.data.student_id} />
                <ProfileField label="Admission ID" value={profile.data.admission_id} />
                <ProfileField label="Date of birth" value={formatDate(profile.data.date_of_birth)} />
                <ProfileField label="Father / guardian" value={profile.data.father_name} />
                <ProfileField label="Mother" value={profile.data.mother_name} />
                <ProfileField label="Gender" value={profile.data.gender} />
                <ProfileField
                  label="Class"
                  value={profile.data.class_name
                    ? `${profile.data.class_name}${profile.data.section ? ` · ${profile.data.section}` : ''}`
                    : null}
                />
                <ProfileField label="Academic year" value={profile.data.academic_year} />
                <ProfileField label="Registered email" value={profile.data.email} />
                <ProfileField label="Contact number" value={profile.data.phone} />
                <ProfileField label="Admission date" value={formatDate(profile.data.admission_date)} />
                <ProfileField label="Address" value={profile.data.address} />
              </dl>
              {!profile.data.student_photo_url ? (
                <p className="mt-3 text-xs text-slate-500">No student photograph is on file.</p>
              ) : null}
            </CardContent>
          </Card>

          <section aria-labelledby="student-fees-heading" className="grid gap-4">
            <div>
              <h2 className="font-heading text-lg font-semibold text-slate-950" id="student-fees-heading">
                Fee details
              </h2>
              <p className="mt-1 text-sm text-slate-600">
                Schedules are drawn from your class and academic year. They do not represent paid or outstanding balances.
              </p>
            </div>

            {fees.isPending ? <LoadingState label="Loading your fee schedules" /> : null}
            {fees.isError ? (
              <ErrorState
                description={toApiError(fees.error).message}
                onRetry={() => void fees.refetch()}
                title="Fee schedules unavailable"
              />
            ) : null}

            {fees.data ? (
              <>
                <Alert>
                  <CalendarDays aria-hidden="true" />
                  <AlertTitle>Payment records are not available</AlertTitle>
                  <AlertDescription>{fees.data.billing_message}</AlertDescription>
                </Alert>
                <div className="grid gap-4 lg:grid-cols-2">
                  {fees.data.admission_fee_structure ? (
                    <AdmissionFeeCard structure={fees.data.admission_fee_structure} />
                  ) : null}
                  {fees.data.monthly_fee_structure ? (
                    <MonthlyFeeCard structure={fees.data.monthly_fee_structure} />
                  ) : null}
                </div>
                {!fees.data.admission_fee_structure && !fees.data.monthly_fee_structure ? (
                  <EmptyState
                    description="The school has not configured a fee schedule for your class and academic year."
                    title="No fee schedules are available"
                  />
                ) : null}
                <Card>
                  <CardHeader>
                    <CardTitle>Monthly fee document</CardTitle>
                    <CardDescription>
                      A fee PDF requires an official invoice and payment ledger for the selected month.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex flex-col gap-3 sm:flex-row sm:items-end">
                    <div className="w-full space-y-1.5 sm:max-w-xs">
                      <label className="text-sm font-medium text-slate-800" htmlFor="fee-document-month">
                        Month
                      </label>
                      <Input
                        id="fee-document-month"
                        onChange={(event) => setSelectedMonth(event.target.value)}
                        type="month"
                        value={selectedMonth}
                      />
                    </div>
                    <Button disabled title="Monthly invoices and payment records are not configured." type="button">
                      <Download aria-hidden="true" />
                      Download Monthly Fee PDF
                    </Button>
                  </CardContent>
                  <p className="px-4 pb-4 text-xs text-slate-500">
                    PDF downloads will be enabled once the school configures invoice and fee-collection records.
                  </p>
                </Card>
              </>
            ) : null}
          </section>
        </div>
      ) : null}
    </>
  )
}
