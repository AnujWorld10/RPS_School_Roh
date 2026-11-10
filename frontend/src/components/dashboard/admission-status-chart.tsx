import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { EmptyState, LoadingState } from '@/components/ui/async-state'
import type { Admission } from '@/features/admissions/admissions-api'
import { toApiError } from '@/lib/api/api-error'

export type AdmissionStatusCount = {
  status: Admission['status']
  label: string
  count: number
}

export default function AdmissionStatusChart({
  counts,
  isLoading,
  error,
  onRetry,
}: {
  counts: AdmissionStatusCount[]
  isLoading: boolean
  error: unknown
  onRetry: () => void
}) {
  const hasData = counts.length > 0
  const hasRecords = counts.some((item) => item.count > 0)
  return (
    <Card>
      <CardHeader>
        <CardTitle>Admission applications by status</CardTitle>
        <p className="text-sm text-slate-500">Live application counts grouped by their actual workflow statuses.</p>
      </CardHeader>
      <CardContent className="grid gap-4">
        {error ? (
          <Alert variant="destructive">
            <AlertTitle>Chart data unavailable</AlertTitle>
            <AlertDescription className="flex flex-col items-start gap-3">
              <span>{toApiError(error).message}</span>
              <Button onClick={onRetry} size="sm" variant="outline">Retry status counts</Button>
            </AlertDescription>
          </Alert>
        ) : null}
        {isLoading ? <LoadingState label="Loading admission status counts" /> : null}
        {!isLoading && !hasData && !error ? (
          <EmptyState title="No admission data" description="No admission status counts are available yet." />
        ) : null}
        {!isLoading && hasData && !hasRecords ? (
          <EmptyState title="No admission applications yet" description="The API returned zero applications across all admission statuses." />
        ) : null}
        {!isLoading && hasData && hasRecords ? (
          <>
            <div aria-label="Admission applications by status chart" className="h-72 w-full" role="img">
              <ResponsiveContainer height="100%" width="100%">
                <BarChart data={counts} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis axisLine={false} dataKey="label" interval={0} tick={{ fontSize: 11 }} tickLine={false} />
                  <YAxis allowDecimals={false} axisLine={false} tickLine={false} />
                  <Tooltip formatter={(value) => [value, 'Applications']} />
                  <Bar dataKey="count" fill="var(--chart-1)" name="Applications" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <ul aria-label="Application counts by status" className="grid grid-cols-2 gap-2 text-sm sm:grid-cols-3">
              {counts.map((item) => (
                <li className="flex items-center justify-between gap-2 rounded-md bg-slate-50 px-3 py-2" key={item.status}>
                  <span>{item.label}</span>
                  <span className="font-semibold tabular-nums">{new Intl.NumberFormat().format(item.count)}</span>
                </li>
              ))}
            </ul>
          </>
        ) : null}
      </CardContent>
    </Card>
  )
}
