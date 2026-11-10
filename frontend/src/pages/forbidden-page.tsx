import { useNavigate } from 'react-router-dom'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { PageHeader } from '@/components/ui/page-header'

export function ForbiddenPage() {
  const navigate = useNavigate()

  return (
    <>
      <PageHeader title="Access restricted" />
      <Alert variant="destructive">
        <AlertTitle>You do not have permission to view this page</AlertTitle>
        <AlertDescription>
          Your account does not include the permission required for this module. If you believe
          this is incorrect, contact a system administrator.
        </AlertDescription>
      </Alert>
      <Button className="mt-5" onClick={() => navigate('/dashboard')} variant="outline">
        Return to dashboard
      </Button>
    </>
  )
}
