import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { ErrorState, LoadingState, SuccessState } from '@/components/ui/async-state'
import { FormDialog } from '@/components/school/form-dialog'
import { admissionsApi, type Admission, type AdmissionDocument, type DocumentType } from '@/features/admissions/admissions-api'
import { toApiError } from '@/lib/api/api-error'
import { useAuth } from '@/features/auth/auth-context'

const documentLabels: Record<DocumentType, string> = {
  progress_report: 'Progress report',
  transfer_certificate: 'Transfer certificate',
  migration_certificate: 'Migration certificate',
  character_certificate: 'Character certificate',
  student_aadhar: 'Student Aadhaar document',
  parent_aadhar: 'Parent Aadhaar document',
}

function documentType(value: string): value is DocumentType {
  return value in documentLabels
}

export function AdmissionDocumentsPanel({ admission }: { admission: Admission }) {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [rejectingDocument, setRejectingDocument] = useState<AdmissionDocument | null>(null)
  const [rejectionReason, setRejectionReason] = useState('')
  const [message, setMessage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [previewName, setPreviewName] = useState('')
  const requiredQuery = useQuery({
    queryKey: ['admissions', 'required-documents'],
    queryFn: admissionsApi.admissions.requiredDocuments,
  })
  const canVerify = user?.permissions?.includes('admissions.verify_documents') ?? false
  const documentsByType = new Map(admission.documents.map((document) => [document.document_type, document]))

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
    }
  }, [previewUrl])

  const viewMutation = useMutation({
    mutationFn: (document: AdmissionDocument) => admissionsApi.admissions.viewDocument(document.id),
    onSuccess: (file, document) => {
      setPreviewUrl(URL.createObjectURL(file))
      setPreviewName(document.file_name)
      setErrorMessage(null)
    },
    onError: (error) => setErrorMessage(toApiError(error).message),
  })
  const verifyMutation = useMutation({
    mutationFn: ({ document, verified, reason }: { document: AdmissionDocument; verified: boolean; reason?: string }) =>
      admissionsApi.admissions.verifyDocument(document.id, verified, reason),
    onSuccess: async (document) => {
      setMessage(document.verification_status === 'VERIFIED' ? 'Document verified.' : 'Document rejected.')
      setErrorMessage(null)
      setRejectingDocument(null)
      setRejectionReason('')
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['admissions', admission.id] }),
        queryClient.invalidateQueries({ queryKey: ['admissions'] }),
      ])
    },
    onError: (error) => setErrorMessage(toApiError(error).message),
  })

  return (
    <section className="grid gap-3">
      <div>
        <h3 className="text-sm font-semibold">Required documents</h3>
        <p className="text-xs text-slate-500">The API requires all six document types uploaded and verified before admission approval and enrollment.</p>
      </div>
      {message ? <SuccessState title="Document workflow updated" description={message} /> : null}
      {errorMessage ? <ErrorState title="Document operation failed" description={errorMessage} /> : null}
      {requiredQuery.isLoading ? <LoadingState label="Loading required document checklist" /> : null}
      {requiredQuery.error ? <ErrorState description={toApiError(requiredQuery.error).message} onRetry={() => void requiredQuery.refetch()} /> : null}
      {requiredQuery.data ? (
        <ul className="grid gap-2">
          {requiredQuery.data.required.map((type) => {
            const document = documentsByType.get(type)
            return (
              <li className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-slate-200 p-3" key={type}>
                <div>
                  <p className="text-sm font-medium">{documentType(type) ? documentLabels[type] : type}</p>
                  {document ? (
                    <p className="text-xs text-slate-600">
                      {document.file_name} · {document.verification_status}
                      {document.rejection_reason ? ` · ${document.rejection_reason}` : ''}
                    </p>
                  ) : <p className="text-xs text-amber-700">Not uploaded</p>}
                </div>
                {document ? (
                  <div className="flex gap-2">
                    <Button
                      disabled={viewMutation.isPending}
                      onClick={() => viewMutation.mutate(document)}
                      size="sm"
                      variant="outline"
                    >
                      View
                    </Button>
                    {canVerify && document.verification_status !== 'VERIFIED' ? (
                      <>
                        <Button disabled={verifyMutation.isPending} onClick={() => verifyMutation.mutate({ document, verified: true })} size="sm" variant="outline">Verify</Button>
                        <Button disabled={verifyMutation.isPending} onClick={() => {
                          setRejectingDocument(document)
                          setRejectionReason('')
                        }} size="sm" variant="destructive">Reject</Button>
                      </>
                    ) : null}
                  </div>
                ) : null}
              </li>
            )
          })}
        </ul>
      ) : null}
      {admission.documents.length ? (
        <p className="text-xs text-slate-500">
          Parents submit or replace documents from the admission portal. Staff can view each file and verify or reject it here.
        </p>
      ) : null}
      <FormDialog
        description={previewName}
        onOpenChange={(open) => {
          if (!open) setPreviewUrl(null)
        }}
        open={previewUrl !== null}
        title="Admission document"
      >
        {previewUrl ? (
          <iframe className="h-[65vh] w-full rounded-md border" src={previewUrl} title={`Preview ${previewName}`} />
        ) : null}
      </FormDialog>
      <FormDialog
        description="A rejection reason is required by the backend."
        onOpenChange={(open) => {
          if (!open) setRejectingDocument(null)
        }}
        open={rejectingDocument !== null}
        title="Reject document"
      >
        <label className="grid gap-2 text-sm font-medium" htmlFor={`document-reason-${admission.id}`}>Rejection reason</label>
        <textarea
          className="min-h-20 rounded-lg border border-input bg-white p-3 text-sm"
          id={`document-reason-${admission.id}`}
          onChange={(event) => setRejectionReason(event.target.value)}
          value={rejectionReason}
        />
        <div className="flex justify-end gap-2">
          <Button onClick={() => setRejectingDocument(null)} type="button" variant="outline">Cancel</Button>
          <Button
            disabled={!rejectionReason.trim() || verifyMutation.isPending || !rejectingDocument}
            onClick={() => {
              if (rejectingDocument) verifyMutation.mutate({ document: rejectingDocument, verified: false, reason: rejectionReason })
            }}
            type="button"
            variant="destructive"
          >
            {verifyMutation.isPending ? 'Rejecting…' : 'Reject document'}
          </Button>
        </div>
      </FormDialog>
    </section>
  )
}
