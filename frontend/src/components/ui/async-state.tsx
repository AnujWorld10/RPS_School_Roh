import { AlertCircle, CheckCircle2, Inbox, LoaderCircle } from 'lucide-react'
import type { ReactNode } from 'react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'

export function LoadingState({ label = 'Loading' }: { label?: string }) {
  return (
    <div
      aria-live="polite"
      className="flex min-h-40 flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-slate-200 bg-white p-8 text-center"
      role="status"
    >
      <LoaderCircle aria-hidden="true" className="size-5 animate-spin text-primary" />
      <p className="text-sm text-slate-600">{label}</p>
    </div>
  )
}

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string
  description: string
  action?: ReactNode
}) {
  return (
    <div className="flex min-h-56 flex-col items-center justify-center rounded-xl border border-dashed border-slate-200 bg-white p-8 text-center">
      <span className="mb-4 inline-flex size-11 items-center justify-center rounded-full bg-slate-100 text-slate-500">
        <Inbox aria-hidden="true" size={20} />
      </span>
      <h2 className="text-sm font-semibold text-slate-900">{title}</h2>
      <p className="mt-1 max-w-md text-sm leading-6 text-slate-500">{description}</p>
      {action ? <div className="mt-5">{action}</div> : null}
    </div>
  )
}

export function ErrorState({
  title = 'Something went wrong',
  description,
  onRetry,
}: {
  title?: string
  description: string
  onRetry?: () => void
}) {
  return (
    <Alert variant="destructive">
      <AlertCircle aria-hidden="true" />
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription className="flex flex-col items-start gap-3">
        <span>{description}</span>
        {onRetry ? (
          <Button onClick={onRetry} size="sm" variant="outline">
            Try again
          </Button>
        ) : null}
      </AlertDescription>
    </Alert>
  )
}

export function SuccessState({
  title,
  description,
}: {
  title: string
  description: string
}) {
  return (
    <Alert className="border-emerald-200 bg-emerald-50 text-emerald-950">
      <CheckCircle2 aria-hidden="true" className="text-emerald-700" />
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription className="text-emerald-800">{description}</AlertDescription>
    </Alert>
  )
}
