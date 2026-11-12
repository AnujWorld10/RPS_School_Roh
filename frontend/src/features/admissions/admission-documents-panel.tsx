import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useRef, useState } from 'react'
import { Download, Maximize, Minimize, Printer, ZoomIn, ZoomOut } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ErrorState, LoadingState, SuccessState } from '@/components/ui/async-state'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { FormDialog } from '@/components/school/form-dialog'
import {
  admissionsApi,
  OPTIONAL_ADMISSION_DOCUMENT_TYPES,
  type Admission,
  type AdmissionDocument,
  type DocumentType,
} from '@/features/admissions/admissions-api'
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
  const [zoom, setZoom] = useState(1)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const previewContainerRef = useRef<HTMLDivElement>(null)
  const previewFrameRef = useRef<HTMLIFrameElement>(null)
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

  useEffect(() => {
    const updateFullscreen = () => setIsFullscreen(document.fullscreenElement === previewContainerRef.current)
    document.addEventListener('fullscreenchange', updateFullscreen)
    return () => document.removeEventListener('fullscreenchange', updateFullscreen)
  }, [])

  const viewMutation = useMutation({
    mutationFn: (document: AdmissionDocument) => admissionsApi.admissions.viewDocument(document.id),
    onSuccess: (file, document) => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
      setPreviewUrl(URL.createObjectURL(file))
      setPreviewName(document.file_name)
      setZoom(1)
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
        <h3 className="text-sm font-semibold">Admission documents</h3>
        <p className="text-xs text-slate-500">Four required documents must be uploaded and verified. Migration and character certificates are optional.</p>
      </div>
      {message ? <SuccessState title="Document workflow updated" description={message} /> : null}
      {errorMessage ? <ErrorState title="Document operation failed" description={errorMessage} /> : null}
      {requiredQuery.isLoading ? <LoadingState label="Loading required document checklist" /> : null}
      {requiredQuery.error ? <ErrorState description={toApiError(requiredQuery.error).message} onRetry={() => void requiredQuery.refetch()} /> : null}
      {requiredQuery.data ? (
        <ul className="grid gap-2">
          {[...new Set([...requiredQuery.data.required, ...OPTIONAL_ADMISSION_DOCUMENT_TYPES])].map((type) => {
            const document = documentsByType.get(type)
            const required = !OPTIONAL_ADMISSION_DOCUMENT_TYPES.includes(type as DocumentType)
            return (
              <li className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-slate-200 p-3" key={type}>
                <div>
                  <p className="text-sm font-medium">
                    {documentType(type) ? documentLabels[type] : type}
                    {!required ? <span className="ml-1 font-normal text-slate-500">(optional)</span> : null}
                  </p>
                  {document ? (
                    <p className="text-xs text-slate-600">
                      {document.file_name} · {document.verification_status}
                      {document.rejection_reason ? ` · ${document.rejection_reason}` : ''}
                    </p>
                  ) : <p className="text-xs text-amber-700">{required ? 'Not uploaded' : 'Not uploaded (optional)'}</p>}
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
      <Dialog
        onOpenChange={(open) => {
          if (!open) {
            setPreviewUrl(null)
            setZoom(1)
          }
        }}
        open={previewUrl !== null}
      >
        <DialogContent className="max-h-[95vh] overflow-y-auto sm:max-w-5xl">
          <DialogHeader>
            <DialogTitle>Admission document</DialogTitle>
            <DialogDescription>{previewName}</DialogDescription>
          </DialogHeader>
          {previewUrl ? (
            <div className="grid gap-3" ref={previewContainerRef}>
              <div className="flex flex-wrap items-center gap-2">
                <Button
                  aria-label="Zoom out"
                  disabled={zoom <= 0.5}
                  onClick={() => setZoom((current) => Math.max(0.5, current - 0.25))}
                  size="sm"
                  type="button"
                  variant="outline"
                >
                  <ZoomOut aria-hidden="true" /> Zoom out
                </Button>
                <span aria-live="polite" className="min-w-14 text-center text-sm">{Math.round(zoom * 100)}%</span>
                <Button
                  aria-label="Zoom in"
                  disabled={zoom >= 2.5}
                  onClick={() => setZoom((current) => Math.min(2.5, current + 0.25))}
                  size="sm"
                  type="button"
                  variant="outline"
                >
                  <ZoomIn aria-hidden="true" /> Zoom in
                </Button>
                <Button
                  onClick={() => {
                    const fullscreen = previewContainerRef.current
                    if (!fullscreen) return
                    const action = document.fullscreenElement
                      ? document.exitFullscreen()
                      : fullscreen.requestFullscreen()
                    void action.catch((error: unknown) => {
                      setErrorMessage(error instanceof Error ? error.message : 'Could not change fullscreen mode.')
                    })
                  }}
                  size="sm"
                  type="button"
                  variant="outline"
                >
                  {isFullscreen ? <Minimize aria-hidden="true" /> : <Maximize aria-hidden="true" />}
                  {isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
                </Button>
                <Button
                  onClick={() => {
                    const link = document.createElement('a')
                    link.href = previewUrl
                    link.download = previewName
                    link.click()
                  }}
                  size="sm"
                  type="button"
                  variant="outline"
                >
                  <Download aria-hidden="true" /> Download
                </Button>
                <Button
                  onClick={() => previewFrameRef.current?.contentWindow?.print()}
                  size="sm"
                  type="button"
                  variant="outline"
                >
                  <Printer aria-hidden="true" /> Print
                </Button>
              </div>
              <div
                className="max-h-[75vh] overflow-auto rounded-md border bg-slate-100 p-2"
                style={{ height: `${75 * zoom}vh`, width: `${100 * zoom}%` }}
              >
                <iframe
                  className="origin-top-left rounded-md bg-white"
                  ref={previewFrameRef}
                  src={previewUrl}
                  style={{ height: '75vh', transform: `scale(${zoom})`, width: '100%' }}
                  title={`Preview ${previewName}`}
                />
              </div>
            </div>
          ) : null}
        </DialogContent>
      </Dialog>
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
