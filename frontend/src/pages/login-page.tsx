import { useState } from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import { Eye, EyeOff, GraduationCap, LoaderCircle, LockKeyhole } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { z } from 'zod'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { PublicSchoolNavigation } from '@/components/layout/public-school-navigation'
import { Card, CardContent, CardDescription, CardHeader } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { toApiError } from '@/lib/api/api-error'
import { useAuth } from '@/features/auth/auth-context'
import { roleLandingPath } from '@/features/auth/permissions'

const portalRoles = ['student', 'parent', 'teacher', 'administration'] as const
type LoginPortal = (typeof portalRoles)[number]

function getLoginPortal(search: string): LoginPortal | undefined {
  const portal = new URLSearchParams(search).get('portal')
  return portalRoles.find((role) => role === portal)
}

type LoginFormValues = {
  email: string
  password: string
}

type LoginLocationState = {
  from?: { pathname?: string }
  sessionExpired?: boolean
  logoutError?: string
}

function safeReturnPath(pathname: string | undefined) {
  return pathname?.startsWith('/') && !pathname.startsWith('//') && pathname !== '/login'
    ? pathname
    : '/dashboard'
}

export function LoginPage() {
  const auth = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [apiError, setApiError] = useState<string | null>(null)
  const [showPassword, setShowPassword] = useState(false)
  const routeState = location.state as LoginLocationState | null
  const portal = getLoginPortal(location.search)
  const loginSchema = z.object({
    email: portal === 'student'
      ? z.string().trim().min(1, 'Enter your student ID.')
      : z.string().email('Enter a valid email address.'),
    password: z.string().min(1, 'Password is required.'),
  })
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  })

  const onSubmit = form.handleSubmit(async (credentials) => {
    setApiError(null)
    try {
      await auth.login(
        portal === 'student'
          ? { student_id: credentials.email, password: credentials.password, portal }
          : { email: credentials.email, password: credentials.password, portal },
      )
      navigate(
        routeState?.from?.pathname
          ? safeReturnPath(routeState.from.pathname)
          : portal === 'student'
            ? '/portal/student'
            : portal === 'parent'
              ? '/portal/parent'
              : portal === 'teacher'
                ? '/portal/teacher'
                : roleLandingPath(auth.user?.roles ?? []),
        { replace: true },
      )
    } catch (error) {
      setApiError(toApiError(error).message)
    }
  })

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-white/95 shadow-sm shadow-slate-900/5">
        <div className="mx-auto max-w-6xl px-4 py-3 sm:px-6">
          <div className="mb-2 flex justify-end">
            <Link
              className="rounded-md bg-teal-50 px-3 py-2 text-sm font-semibold text-teal-900 hover:bg-teal-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700"
              to="/apply"
            >
              Open the public admission portal
            </Link>
          </div>
          <PublicSchoolNavigation />
        </div>
      </header>
      <main className="flex min-h-[calc(100vh-3.5rem)] items-center justify-center px-4 py-10">
        <div className="w-full max-w-md">
        <div className="mb-6 flex items-center justify-center gap-3 text-teal-900">
          <span className="flex size-11 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-md shadow-teal-900/20">
            <GraduationCap aria-hidden="true" size={23} />
          </span>
          <span className="text-lg font-semibold text-slate-950">RPS School Management</span>
        </div>

        <Card>
          <CardHeader>
            <h1 className="font-heading text-xl font-medium leading-snug">Sign in</h1>
              <CardDescription>
              {portal === 'student'
                ? 'Sign in with the student ID issued after admission and your password.'
                : portal
                    ? `Sign in to the ${portal === 'administration' ? 'administration' : portal} portal with your school account.`
                    : 'Use your school management account to continue.'}
            </CardDescription>
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
                  {portal === 'student' ? 'Student ID' : 'Email'}
                </label>
                <Input
                  autoComplete="username"
                  aria-describedby={form.formState.errors.email ? 'login-email-error' : undefined}
                  aria-invalid={Boolean(form.formState.errors.email)}
                  id="login-email"
                  inputMode={portal === 'student' ? 'text' : 'email'}
                  placeholder={portal === 'student' ? 'RPS00001' : undefined}
                  type={portal === 'student' ? 'text' : 'email'}
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
                <div className="relative">
                  <Input
                    autoComplete="current-password"
                    aria-describedby={
                      form.formState.errors.password ? 'login-password-error' : undefined
                    }
                    aria-invalid={Boolean(form.formState.errors.password)}
                    className="pr-10"
                    id="login-password"
                    type={showPassword ? 'text' : 'password'}
                    {...form.register('password')}
                  />
                  <Button
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    className="absolute right-1 top-0"
                    onClick={() => setShowPassword((visible) => !visible)}
                    size="icon-sm"
                    type="button"
                    variant="ghost"
                  >
                    {showPassword
                      ? <EyeOff aria-hidden="true" />
                      : <Eye aria-hidden="true" />}
                  </Button>
                </div>
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
            {portal === 'student' ? (
              <p className="mt-5 text-center text-sm text-slate-600">
                New student?{' '}
                <Link className="font-semibold text-teal-800 underline" to="/student/register">
                  Sign up with your admission details
                </Link>
              </p>
            ) : null}
          </CardContent>
        </Card>
        </div>
      </main>
    </div>
  )
}
