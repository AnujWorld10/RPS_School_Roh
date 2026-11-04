import { Route, Routes } from 'react-router-dom'
import {
  RequireAuthentication,
  RequirePermission,
  RedirectAuthenticatedUser,
} from '@/components/auth/route-guards'
import { AppShell } from '@/components/layout/app-shell'
import { EmptyState } from '@/components/ui/async-state'
import { PageHeader } from '@/components/ui/page-header'
import { LoginPage } from '@/pages/login-page'
import { ModulePage } from '@/pages/module-page'
import { StudentsPage } from '@/pages/students-page'
import { TeachersPage } from '@/pages/teachers-page'
import { ClassesPage } from '@/pages/classes-page'
import { SubjectsPage } from '@/pages/subjects-page'

function DashboardPage() {
  return (
    <>
      <PageHeader
        description="A shared workspace for school administration. Live summaries will be added when dashboard data is integrated."
        title="Dashboard"
      />
      <EmptyState
        description="No school data is loaded in this phase. The frontend foundation is ready for future API integration."
        title="Your workspace is ready"
      />
    </>
  )
}

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
      <Route element={<RedirectAuthenticatedUser />}>
        <Route element={<LoginPage />} path="/login" />
      </Route>
      <Route element={<RequireAuthentication />}>
        <Route element={<AppShell />}>
          <Route element={<DashboardPage />} path="/" />
          <Route element={<RequirePermission anyOf={['students.read']}><StudentsPage /></RequirePermission>} path="/students" />
          <Route element={<RequirePermission anyOf={['teachers.read']}><TeachersPage /></RequirePermission>} path="/teachers" />
          <Route element={<RequirePermission anyOf={['classes.read']}><ClassesPage /></RequirePermission>} path="/classes" />
          <Route element={<RequirePermission anyOf={['subjects.read']}><SubjectsPage /></RequirePermission>} path="/subjects" />
          <Route
            element={
              <RequirePermission anyOf={['inquiries.read']}>
                <ModulePage
                  description="Student admission inquiry review and status transitions."
                  title="Inquiries"
                />
              </RequirePermission>
            }
            path="/inquiries"
          />
          <Route
            element={
              <RequirePermission anyOf={['interviews.read']}>
                <ModulePage
                  description="Interview scheduling and outcome recording."
                  title="Interviews"
                />
              </RequirePermission>
            }
            path="/interviews"
          />
          <Route
            element={
              <RequirePermission anyOf={['admissions.read']}>
                <ModulePage
                  description="Inquiry-linked admission applications, approval, rejection, and enrollment."
                  title="Admissions"
                />
              </RequirePermission>
            }
            path="/admissions"
          />
          <Route
            element={
              <RequirePermission anyOf={['admissions.update', 'admissions.verify_documents']}>
                <ModulePage
                  description="Admission document upload metadata and staff verification workflows."
                  title="Documents"
                />
              </RequirePermission>
            }
            path="/documents"
          />
          <Route
            element={
              <RequirePermission anyOf={['teachers.update']}>
                <ModulePage
                  description="Teacher attendance recording. Attendance history is not available in the current API."
                  title="Teacher attendance"
                />
              </RequirePermission>
            }
            path="/teacher-attendance"
          />
          <Route
            element={
              <RequirePermission anyOf={['teachers.salary.read', 'teachers.salary.pay']}>
                <ModulePage
                  description="Teacher salary details and salary payment recording."
                  title="Salary payments"
                />
              </RequirePermission>
            }
            path="/salary"
          />
          <Route element={<NotFoundPage />} path="*" />
        </Route>
      </Route>
    </Routes>
  )
}

export default App
