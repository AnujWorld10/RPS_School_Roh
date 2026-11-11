import { lazy, Suspense } from 'react'
import { Route, Routes } from 'react-router-dom'
import {
  RequireAuthentication,
  RequirePermission,
  RequireRole,
  RedirectAuthenticatedUser,
} from '@/components/auth/route-guards'
import { AppShell } from '@/components/layout/app-shell'
import { PublicSchoolPage } from '@/components/layout/public-school-navigation'
import { publicSchoolPages } from '@/components/layout/public-school-pages'
import { EmptyState, LoadingState } from '@/components/ui/async-state'
import { PageHeader } from '@/components/ui/page-header'
import {
  PublicAdmissionSubmissionPage,
  PublicInquiryPage,
  PublicInquiryStatusPage,
  PublicInquiryUpdatePage,
  PublicPortalLayout,
} from '@/pages/public-admissions-pages'

const DashboardPage = lazy(() =>
  import('@/pages/dashboard-page').then(({ DashboardPage }) => ({ default: DashboardPage })),
)
const LoginPage = lazy(() =>
  import('@/pages/login-page').then(({ LoginPage }) => ({ default: LoginPage })),
)
const StudentRegistrationPage = lazy(() =>
  import('@/pages/student-registration-page').then(
    ({ StudentRegistrationPage }) => ({ default: StudentRegistrationPage }),
  ),
)
const StudentPortalPage = lazy(() =>
  import('@/pages/student-portal-page').then(
    ({ StudentPortalPage }) => ({ default: StudentPortalPage }),
  ),
)
const StudentsPage = lazy(() =>
  import('@/pages/students-page').then(({ StudentsPage }) => ({ default: StudentsPage })),
)
const TeachersPage = lazy(() =>
  import('@/pages/teachers-page').then(({ TeachersPage }) => ({ default: TeachersPage })),
)
const ClassesPage = lazy(() =>
  import('@/pages/classes-page').then(({ ClassesPage }) => ({ default: ClassesPage })),
)
const SubjectsPage = lazy(() =>
  import('@/pages/subjects-page').then(({ SubjectsPage }) => ({ default: SubjectsPage })),
)
const InquiriesPage = lazy(() =>
  import('@/pages/inquiries-page').then(({ InquiriesPage }) => ({ default: InquiriesPage })),
)
const InterviewsPage = lazy(() =>
  import('@/pages/interviews-page').then(({ InterviewsPage }) => ({ default: InterviewsPage })),
)
const AdmissionsPage = lazy(() =>
  import('@/pages/admissions-page').then(({ AdmissionsPage }) => ({ default: AdmissionsPage })),
)
const DocumentsPage = lazy(() =>
  import('@/pages/admissions-page').then(({ DocumentsPage }) => ({ default: DocumentsPage })),
)
const RolePortalPage = lazy(() =>
  import('@/pages/role-portal-page').then(({ RolePortalPage }) => ({ default: RolePortalPage })),
)
const SchoolEventsPage = lazy(() =>
  import('@/pages/role-portal-page').then(({ SchoolEventsPage }) => ({ default: SchoolEventsPage })),
)
function NotFoundPage() {
  return (
    <>
      <PageHeader title="Page not found" />
      <EmptyState
        description="The page you requested is not part of this application."
        title="We couldn't find that page"
      />
    </>
  )
}

function App() {
  return (
    <Routes>
      <Route element={<PublicSchoolPage title="Home" />} path="/" />
      <Route element={<RedirectAuthenticatedUser />}>
        <Route
          element={
            <Suspense fallback={<LoadingState label="Loading sign-in" />}>
              <LoginPage />
            </Suspense>
          }
          path="/login"
        />
      </Route>
      <Route
        element={
          <Suspense fallback={<LoadingState label="Loading student registration" />}>
            <StudentRegistrationPage />
          </Suspense>
        }
        path="/student/register"
      />
      {Object.entries(publicSchoolPages).map(([path, title]) => (
        <Route
          element={<PublicSchoolPage title={title} />}
          key={path}
          path={path}
        />
      ))}
      <Route element={<PublicPortalLayout />}>
        <Route element={<PublicInquiryPage />} path="/apply" />
        <Route element={<PublicInquiryStatusPage />} path="/application/status" />
        <Route element={<PublicInquiryUpdatePage />} path="/application/update" />
        <Route element={<PublicAdmissionSubmissionPage />} path="/application/submit" />
      </Route>
      <Route element={<RequireAuthentication />}>
        <Route element={<AppShell />}>
          <Route element={<DashboardPage />} path="/dashboard" />
          <Route element={<RequirePermission anyOf={['students.read']}><StudentsPage /></RequirePermission>} path="/students" />
          <Route element={<RequirePermission anyOf={['teachers.read']}><TeachersPage /></RequirePermission>} path="/teachers" />
          <Route element={<RequirePermission anyOf={['classes.read']}><ClassesPage /></RequirePermission>} path="/classes" />
          <Route element={<RequirePermission anyOf={['subjects.read']}><SubjectsPage /></RequirePermission>} path="/subjects" />
          <Route
            element={
              <RequirePermission anyOf={['inquiries.read']}><InquiriesPage /></RequirePermission>
            }
            path="/inquiries"
          />
          <Route
            element={
              <RequirePermission allOf={['interviews.read', 'inquiries.read']}><InterviewsPage /></RequirePermission>
            }
            path="/interviews"
          />
          <Route
            element={
              <RequirePermission anyOf={['admissions.read']}><AdmissionsPage /></RequirePermission>
            }
            path="/admissions"
          />
          <Route
            element={
              <RequirePermission anyOf={['admissions.read']}><DocumentsPage /></RequirePermission>
            }
            path="/documents"
          />
          <Route
            element={
              <RequireRole anyOf={['STUDENT']}>
                <Suspense fallback={<LoadingState label="Loading student dashboard" />}>
                  <StudentPortalPage />
                </Suspense>
              </RequireRole>
            }
            path="/portal/student"
          />
          <Route
            element={<RequireRole anyOf={['PARENT']}><RolePortalPage role="parent" /></RequireRole>}
            path="/portal/parent"
          />
          <Route
            element={<RequireRole anyOf={['TEACHER']}><RolePortalPage role="teacher" /></RequireRole>}
            path="/portal/teacher"
          />
          <Route
            element={<RequirePermission anyOf={['events.read']}><SchoolEventsPage /></RequirePermission>}
            path="/events"
          />
          <Route element={<NotFoundPage />} path="*" />
        </Route>
      </Route>
    </Routes>
  )
}

export default App
