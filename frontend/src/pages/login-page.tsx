import { useState } from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import { GraduationCap, LoaderCircle, LockKeyhole } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router-dom'
import { z } from 'zod'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { toApiError } from '@/lib/api/api-error'
import { useAuth } from '@/features/auth/auth-context'

const loginSchema = z.object({
  email: z.string().email('Enter a valid email address.'),
  password: z.string().min(1, 'Password is required.'),
})

type LoginFormValues = z.infer<typeof loginSchema>

type LoginLocationState = {
  from?: { pathname?: string }
  sessionExpired?: boolean
  logoutError?: string
}

function safeReturnPath(pathname: string | undefined) {
  return pathname?.startsWith('/') && !pathname.startsWith('//') && pathname !== '/login'
    ? pathname
    : '/'
}

export function LoginPage() {
  const auth = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [apiError, setApiError] = useState<string | null>(null)
  const routeState = location.state as LoginLocationState | null
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  })

  const onSubmit = form.handleSubmit(async (credentials) => {
    setApiError(null)
    try {
      await auth.login(credentials)
      navigate(safeReturnPath(routeState?.from?.pathname), { replace: true })
    } catch (error) {
      setApiError(toApiError(error).message)
    }
  })

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-10">
      <div className="w-full max-w-md">
        <div className="mb-6 flex items-center justify-center gap-3 text-indigo-800">
          <span className="flex size-11 items-center justify-center rounded-xl bg-indigo-700 text-white">
            <GraduationCap aria-hidden="true" size={23} />
          </span>
          <span className="text-lg font-semibold text-slate-950">RPS School Management</span>
        </div>

        <Card>
          <CardHeader>
            <h1 className="font-heading text-xl font-medium leading-snug">Sign in</h1>
            <CardDescription>Use your school management account to continue.</CardDescription>
          </CardHeader>
          <CardContent>
            {routeState?.sessionExpired ? (
              <Alert className="mb-5">
                <LockKeyhole aria-hidden="true" />
                <AlertTitle>Session ended</AlertTitle>
                <AlertDescription>
                  Your session could not be renewed. Sign in again to continue.
                </AlertDescription>
              </Alert>
            ) : null}
            {routeState?.logoutError ? (
              <Alert className="mb-5" variant="destructive">
                <AlertTitle>Signed out locally</AlertTitle>
                <AlertDescription>{routeState.logoutError}</AlertDescription>
              </Alert>
            ) : null}
            {apiError ? (
              <Alert className="mb-5" variant="destructive" role="alert">
                <AlertTitle>Sign-in failed</AlertTitle>
                <AlertDescription>{apiError}</AlertDescription>
              </Alert>
            ) : null}

            <form className="space-y-4" noValidate onSubmit={onSubmit}>
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-800" htmlFor="login-email">
                  Email
                </label>
                <Input
                  autoComplete="username"
                  aria-describedby={form.formState.errors.email ? 'login-email-error' : undefined}
                  aria-invalid={Boolean(form.formState.errors.email)}
                  id="login-email"
                  inputMode="email"
                  type="email"
                  {...form.register('email')}
                />
                {form.formState.errors.email ? (
                  <p className="text-sm text-destructive" id="login-email-error">
                    {form.formState.errors.email.message}
                  </p>
                ) : null}
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-800" htmlFor="login-password">
                  Password
                </label>
                <Input
                  autoComplete="current-password"
                  aria-describedby={
                    form.formState.errors.password ? 'login-password-error' : undefined
                  }
                  aria-invalid={Boolean(form.formState.errors.password)}
                  id="login-password"
                  type="password"
                  {...form.register('password')}
                />
                {form.formState.errors.password ? (
                  <p className="text-sm text-destructive" id="login-password-error">
                    {form.formState.errors.password.message}
                  </p>
                ) : null}
              </div>

              <Button
                className="w-full"
                disabled={form.formState.isSubmitting || auth.isLoggingIn}
                type="submit"
              >
                {form.formState.isSubmitting || auth.isLoggingIn ? (
                  <LoaderCircle aria-hidden="true" className="animate-spin" />
                ) : null}
                Sign in
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </main>
  )
}
