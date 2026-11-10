import { useState } from 'react'
import { zodResolver } from '@hookform/resolvers/zod'
import { Eye, EyeOff, GraduationCap, LoaderCircle } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'
import { z } from 'zod'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { PublicSchoolNavigation } from '@/components/layout/public-school-navigation'
import { Card, CardContent, CardDescription, CardHeader } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { registerStudentPortal } from '@/features/auth/auth-api'
import { toApiError } from '@/lib/api/api-error'

const passwordPolicy =
  /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()\-_=+[\]{}|;:,.<>?]).{8,128}$/

const registrationSchema = z.object({
  admission_id: z.string().trim().min(1, 'Enter the admission ID issued by the school.'),
  email: z.string().trim().email('Enter a valid registered email address.'),
  password: z.string().regex(
    passwordPolicy,
    'Use at least 8 characters with uppercase, lowercase, a number, and a special character.',
  ),
  confirm_password: z.string().min(1, 'Confirm your password.'),
}).refine((values) => values.password === values.confirm_password, {
  message: 'Passwords do not match.',
  path: ['confirm_password'],
})

type RegistrationValues = z.infer<typeof registrationSchema>

export function StudentRegistrationPage() {
  const [apiError, setApiError] = useState<string | null>(null)
  const [studentId, setStudentId] = useState<string | null>(null)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmation, setShowConfirmation] = useState(false)
  const form = useForm<RegistrationValues>({
    resolver: zodResolver(registrationSchema),
    defaultValues: {
      admission_id: '',
      email: '',
      password: '',
      confirm_password: '',
    },
  })

  const onSubmit = form.handleSubmit(async (values) => {
    setApiError(null)
    try {
      const result = await registerStudentPortal(values)
      setStudentId(result.student_id)
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
              <h1 className="font-heading text-xl font-medium leading-snug">
                Create a student account
              </h1>
              <CardDescription>
                Registration is available only after the school completes your admission.
                Use the admission ID and email address on your school record.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {studentId ? (
                <Alert className="border-emerald-200 bg-emerald-50 text-emerald-950" role="status">
                  <AlertTitle>Student account created</AlertTitle>
                  <AlertDescription className="space-y-3 text-emerald-900">
                    <p>
                      Your student ID is <strong className="text-lg">{studentId}</strong>.
                      Keep it safe; you will use it to sign in.
                    </p>
                    <Link
                      className="inline-flex min-h-9 items-center rounded-md bg-teal-900 px-3 py-2 font-semibold text-white hover:bg-teal-800"
                      to="/login?portal=student"
                    >
                      Continue to student login
                    </Link>
                  </AlertDescription>
                </Alert>
              ) : (
                <>
                  {apiError ? (
                    <Alert className="mb-5" variant="destructive" role="alert">
                      <AlertTitle>Registration could not be completed</AlertTitle>
                      <AlertDescription>{apiError}</AlertDescription>
                    </Alert>
                  ) : null}
                  <form className="space-y-4" noValidate onSubmit={onSubmit}>
                    <div className="space-y-1.5">
                      <label className="text-sm font-medium text-slate-800" htmlFor="student-admission-id">
                        Admission ID / Student ID
                      </label>
                      <Input
                        autoComplete="off"
                        aria-describedby={form.formState.errors.admission_id ? 'student-admission-id-error' : undefined}
                        aria-invalid={Boolean(form.formState.errors.admission_id)}
                        id="student-admission-id"
                        placeholder="RPS00001"
                        {...form.register('admission_id')}
                      />
                      {form.formState.errors.admission_id ? (
                        <p className="text-sm text-destructive" id="student-admission-id-error">
                          {form.formState.errors.admission_id.message}
                        </p>
                      ) : null}
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-sm font-medium text-slate-800" htmlFor="student-registration-email">
                        Registered email address
                      </label>
                      <Input
                        autoComplete="email"
                        aria-describedby={form.formState.errors.email ? 'student-registration-email-error' : undefined}
                        aria-invalid={Boolean(form.formState.errors.email)}
                        id="student-registration-email"
                        inputMode="email"
                        type="email"
                        {...form.register('email')}
                      />
                      {form.formState.errors.email ? (
                        <p className="text-sm text-destructive" id="student-registration-email-error">
                          {form.formState.errors.email.message}
                        </p>
                      ) : null}
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-sm font-medium text-slate-800" htmlFor="student-registration-password">
                        Create password
                      </label>
                      <div className="relative">
                        <Input
                          autoComplete="new-password"
                          aria-describedby={form.formState.errors.password ? 'student-registration-password-error' : undefined}
                          aria-invalid={Boolean(form.formState.errors.password)}
                          className="pr-10"
                          id="student-registration-password"
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
                          {showPassword ? <EyeOff aria-hidden="true" /> : <Eye aria-hidden="true" />}
                        </Button>
                      </div>
                      {form.formState.errors.password ? (
                        <p className="text-sm text-destructive" id="student-registration-password-error">
                          {form.formState.errors.password.message}
                        </p>
                      ) : null}
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-sm font-medium text-slate-800" htmlFor="student-confirm-password">
                        Confirm password
                      </label>
                      <div className="relative">
                        <Input
                          autoComplete="new-password"
                          aria-describedby={form.formState.errors.confirm_password ? 'student-confirm-password-error' : undefined}
                          aria-invalid={Boolean(form.formState.errors.confirm_password)}
                          className="pr-10"
                          id="student-confirm-password"
                          type={showConfirmation ? 'text' : 'password'}
                          {...form.register('confirm_password')}
                        />
                        <Button
                          aria-label={showConfirmation ? 'Hide confirmation password' : 'Show confirmation password'}
                          className="absolute right-1 top-0"
                          onClick={() => setShowConfirmation((visible) => !visible)}
                          size="icon-sm"
                          type="button"
                          variant="ghost"
                        >
                          {showConfirmation ? <EyeOff aria-hidden="true" /> : <Eye aria-hidden="true" />}
                        </Button>
                      </div>
                      {form.formState.errors.confirm_password ? (
                        <p className="text-sm text-destructive" id="student-confirm-password-error">
                          {form.formState.errors.confirm_password.message}
                        </p>
                      ) : null}
                    </div>

                    <Button className="w-full" disabled={form.formState.isSubmitting} type="submit">
                      {form.formState.isSubmitting ? (
                        <LoaderCircle aria-hidden="true" className="animate-spin" />
                      ) : null}
                      Create student account
                    </Button>
                  </form>
                  <p className="mt-5 text-center text-sm text-slate-600">
                    Already registered?{' '}
                    <Link className="font-semibold text-teal-800 underline" to="/login?portal=student">
                      Sign in
                    </Link>
                  </p>
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
