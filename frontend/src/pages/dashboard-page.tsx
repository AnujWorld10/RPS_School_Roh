import { lazy, Suspense } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  BookOpen,
  CalendarClock,
  ClipboardList,
  FileCheck2,
  GraduationCap,
  School,
  Users,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/async-state'
import { PageHeader } from '@/components/ui/page-header'
import { useAuth } from '@/features/auth/auth-context'
import { admissionsApi, type Admission, type Inquiry } from '@/features/admissions/admissions-api'
import { dashboardApi, type DashboardAdmissionStatus, type DashboardSummary } from '@/features/dashboard/dashboard-api'
import { toApiError } from '@/lib/api/api-error'

const AdmissionStatusChart = lazy(() => import('@/components/dashboard/admission-status-chart'))
const inquiryListParams = { page: 1, limit: 5, sort_by: 'created_at', sort_order: 'desc' as const }

const admissionStatuses: { status: Admission['status']; label: string }[] = [
  { status: 'draft', label: 'Draft' },
  { status: 'submitted', label: 'Submitted' },
  { status: 'document_pending', label: 'Documents pending' },
  { status: 'document_verification', label: 'Document review' },
  { status: 'approved', label: 'Approved' },
  { status: 'rejected', label: 'Rejected' },
]

type SummaryMetricKey = Exclude<keyof DashboardSummary, 'school_timezone' | 'admissions_by_status' | 'upcoming_interviews'>
type MetricDefinition = {
  key: SummaryMetricKey
  label: string
  permission: string
  icon: typeof Users
  description?: string
}

function formatCount(count: number) {
  return new Intl.NumberFormat().format(count)
}

function MetricCard({
  metric,
  value,
  isLoading,
  error,
  onRetry,
}: {
  metric: MetricDefinition
  value: number | null | undefined
  isLoading: boolean
  error: unknown
  onRetry: () => void
}) {
  const Icon = metric.icon
  return (
    <Card className="border border-border/80 border-t-2 border-t-primary/70 bg-white shadow-md shadow-slate-900/5 transition-shadow hover:shadow-lg hover:shadow-slate-900/10">
      <CardHeader className="flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{metric.label}</CardTitle>
        <span className="flex size-9 items-center justify-center rounded-xl bg-teal-50 text-teal-800">
          <Icon aria-hidden="true" className="size-[18px]" />
        </span>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p aria-live="polite" className="text-sm text-slate-500">Loading…</p>
        ) : error ? (
          <div className="grid gap-2">
            <p className="text-sm text-destructive">Unavailable: {toApiError(error).message}</p>
            <Button className="w-fit" onClick={onRetry} size="sm" variant="outline">Retry</Button>
          </div>
        ) : value === null || value === undefined ? (
          <p className="text-sm text-slate-500">Not provided by the API.</p>
        ) : (
          <>
            <p className="text-3xl font-semibold tracking-tight">{formatCount(value)}</p>
            {metric.description ? <p className="mt-1 text-xs text-slate-500">{metric.description}</p> : null}
          </>
        )}
      </CardContent>
    </Card>
  )
}

function RecentInquiries({
  data,
  isLoading,
  error,
  onRetry,
}: {
  data: { items: Inquiry[] } | undefined
  isLoading: boolean
  error: unknown
  onRetry: () => void
}) {
  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between">
        <div>
          <CardTitle>Recent inquiries</CardTitle>
          <p className="mt-1 text-sm text-slate-500">Latest records returned by the inquiry list API.</p>
        </div>
        <Link
          className="inline-flex h-7 items-center justify-center rounded-lg border border-border px-2.5 text-xs font-medium hover:bg-teal-50 hover:text-teal-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          to="/inquiries"
        >
          View inquiries
        </Link>
      </CardHeader>
      <CardContent>
        {isLoading ? <LoadingState label="Loading recent inquiries" /> : null}
        {error ? <ErrorState description={toApiError(error).message} onRetry={onRetry} /> : null}
        {data?.items.length === 0 ? (
          <EmptyState title="No inquiries yet" description="New inquiries will appear here when the API returns them." />
        ) : null}
        {data && data.items.length > 0 ? (
          <ul className="divide-y divide-slate-100">
            {data.items.map((item) => (
              <li className="flex flex-wrap items-center justify-between gap-2 py-3 first:pt-0 last:pb-0" key={item.id}>
                <div>
                  <p className="font-medium">{item.first_name} {item.last_name}</p>
                  <p className="text-xs text-slate-500">{item.inquiry_code} · {new Date(item.created_at).toLocaleDateString()}</p>
                </div>
                <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium">{item.status}</span>
              </li>
            ))}
          </ul>
        ) : null}
      </CardContent>
    </Card>
  )
}

function UpcomingInterviews({
  data,
  count,
  timezone,
}: {
  data: DashboardSummary['upcoming_interviews']
  count: number
  timezone: string
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Upcoming interviews</CardTitle>
        <p className="text-sm text-slate-500">Next scheduled interviews · school local time ({timezone})</p>
      </CardHeader>
      <CardContent>
        {count === 0 ? (
          <EmptyState title="No upcoming interviews" description="There are no scheduled interviews from the current school-local time onward." />
        ) : data === null ? (
          <p className="text-sm text-slate-500">Interview details are not available with the current permissions.</p>
        ) : data.length === 0 ? (
          <ErrorState description="The API reported upcoming interviews but returned no interview details." />
        ) : (
          <>
            <ul className="divide-y divide-slate-100">
              {data.map((interview) => (
                <li className="grid gap-1 py-3 first:pt-0 last:pb-0" key={interview.id}>
                  <p className="font-medium">{interview.student_name} · {interview.inquiry_code}</p>
                  <p className="text-sm text-slate-600">
                    {interview.schedule_date} at {interview.schedule_time} · {interview.mode}
                  </p>
                  <p className="text-xs text-slate-500">{interview.location}</p>
                </li>
              ))}
            </ul>
            {count > data.length ? <p className="mt-3 text-xs text-slate-500">Showing the next {data.length} of {formatCount(count)} interviews.</p> : null}
          </>
        )}
      </CardContent>
    </Card>
  )
}

export function DashboardPage() {
  const { user } = useAuth()
  const permissions = new Set(user?.permissions ?? [])
  const canReadInquiries = permissions.has('inquiries.read')
  const canReadAdmissions = permissions.has('admissions.read')
  const canReadInterviews = permissions.has('interviews.read')
  const canReadUpcomingInterviewDetails = canReadInterviews && canReadInquiries
  const metrics: MetricDefinition[] = [
    { key: 'student_count', label: 'Students', permission: 'students.read', icon: GraduationCap },
    { key: 'teacher_count', label: 'Teachers', permission: 'teachers.read', icon: Users },
    { key: 'class_count', label: 'Classes', permission: 'classes.read', icon: School },
    { key: 'subject_count', label: 'Subjects', permission: 'subjects.read', icon: BookOpen },
    { key: 'inquiry_count', label: 'Inquiries', permission: 'inquiries.read', icon: ClipboardList },
    {
      key: 'pending_admission_count',
      label: 'Pending admissions',
      permission: 'admissions.read',
      icon: FileCheck2,
      description: 'Draft, submitted, documents pending, or in document review.',
    },
    { key: 'upcoming_interview_count', label: 'Upcoming interviews', permission: 'interviews.read', icon: CalendarClock },
  ]
  const visibleMetrics = metrics.filter((metric) => permissions.has(metric.permission))
  const canReadAnyDashboardMetric = visibleMetrics.length > 0
  const summaryQuery = useQuery({
    queryKey: ['dashboard', 'summary'],
    queryFn: dashboardApi.summary,
    enabled: canReadAnyDashboardMetric,
  })
  const inquiriesQuery = useQuery({
    queryKey: ['dashboard', 'recent-inquiries'],
    queryFn: () => admissionsApi.inquiries.list(inquiryListParams, {}),
    enabled: canReadInquiries,
  })
  const summary = summaryQuery.data
  const chartCounts = summary?.admissions_by_status
    ? admissionStatuses.map((item) => ({
      ...item,
      count: summary.admissions_by_status?.[item.status as DashboardAdmissionStatus] ?? 0,
    }))
    : []
  const quickLinks = [
    { href: '/students', label: 'Manage students', permission: 'students.read', icon: GraduationCap },
    { href: '/teachers', label: 'Manage teachers', permission: 'teachers.read', icon: Users },
    { href: '/classes', label: 'Manage classes', permission: 'classes.read', icon: School },
    { href: '/inquiries', label: 'Review inquiries', permission: 'inquiries.read', icon: ClipboardList },
    { href: '/interviews', label: 'Manage interviews', permission: 'interviews.read', icon: CalendarClock },
    { href: '/admissions', label: 'Review applications', permission: 'admissions.read', icon: FileCheck2 },
  ].filter((item) => permissions.has(item.permission) && (item.href !== '/interviews' || canReadInquiries))

  return (
    <div className="grid gap-6">
      <PageHeader
        description="Live counts are read from the school management APIs and limited to the data your account can access."
        title="Dashboard"
      />
      {!canReadAnyDashboardMetric ? (
        <EmptyState title="No dashboard metrics available" description="Your account does not have permission to read the school or admissions summary APIs." />
      ) : (
        <>
          {summaryQuery.error ? (
            <ErrorState title="Dashboard summary unavailable" description={toApiError(summaryQuery.error).message} onRetry={() => void summaryQuery.refetch()} />
          ) : null}
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {visibleMetrics.map((metric) => (
              <MetricCard
                error={summaryQuery.error}
                isLoading={summaryQuery.isLoading}
                key={metric.key}
                metric={metric}
                onRetry={() => void summaryQuery.refetch()}
                value={summary?.[metric.key]}
              />
            ))}
          </div>
          <div className="grid gap-6 xl:grid-cols-2">
            {canReadAdmissions ? (
              <Suspense fallback={<LoadingState label="Loading admissions chart" />}>
                <AdmissionStatusChart
                  counts={chartCounts}
                  error={summaryQuery.error}
                  isLoading={summaryQuery.isLoading}
                  onRetry={() => void summaryQuery.refetch()}
                />
              </Suspense>
            ) : null}
            {canReadInquiries ? (
              <RecentInquiries
                data={inquiriesQuery.data}
                error={inquiriesQuery.error}
                isLoading={inquiriesQuery.isLoading}
                onRetry={() => void inquiriesQuery.refetch()}
              />
            ) : null}
            {canReadUpcomingInterviewDetails && summary ? (
              <UpcomingInterviews
                count={summary.upcoming_interview_count ?? 0}
                data={summary.upcoming_interviews}
                timezone={summary.school_timezone}
              />
            ) : null}
          </div>
          {quickLinks.length > 0 ? (
            <section aria-labelledby="dashboard-quick-links" className="grid gap-3">
              <h2 className="text-lg font-semibold" id="dashboard-quick-links">Quick access</h2>
              <div className="flex flex-wrap gap-3">
                {quickLinks.map((item) => {
                  const Icon = item.icon
                  return (
                    <Link
                      className="inline-flex h-8 items-center justify-center gap-2 rounded-lg border border-border bg-white px-2.5 text-sm font-medium shadow-sm transition-colors hover:border-teal-200 hover:bg-teal-50 hover:text-teal-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                      key={item.href}
                      to={item.href}
                    >
                      <Icon aria-hidden="true" />{item.label}
                    </Link>
                  )
                })}
              </div>
            </section>
          ) : null}
        </>
      )}
    </div>
  )
}
