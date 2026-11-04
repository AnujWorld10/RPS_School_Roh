import { LoaderCircle } from 'lucide-react'
import { useState } from 'react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { toApiError } from '@/lib/api/api-error'
import type { ReactElement } from 'react'

type ConfirmDialogProps = {
  title: string
  description: string
  confirmLabel?: string
  trigger: ReactElement
  onConfirm: () => void | Promise<void>
  destructive?: boolean
}

export function ConfirmDialog({
  title,
  description,
  confirmLabel = 'Continue',
  trigger,
  onConfirm,
  destructive = false,
}: ConfirmDialogProps) {
  const [open, setOpen] = useState(false)
  const [isPending, setIsPending] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  async function confirm() {
    setIsPending(true)
    try {
      await onConfirm()
      setOpen(false)
    } catch (error) {
      setErrorMessage(toApiError(error).message)
    } finally {
      setIsPending(false)
    }
  }

  return (
    <Dialog
      onOpenChange={(nextOpen) => {
        setOpen(nextOpen)
        if (nextOpen) setErrorMessage(null)
      }}
      open={open}
    >
      <DialogTrigger render={trigger} />
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{description}</DialogDescription>
        </DialogHeader>
        {errorMessage ? (
          <Alert variant="destructive">
            <AlertDescription>{errorMessage}</AlertDescription>
          </Alert>
        ) : null}
        <DialogFooter>
          <Button
            disabled={isPending}
            onClick={() => void confirm()}
            type="button"
            variant={destructive ? 'destructive' : 'default'}
          >
            {isPending ? <LoaderCircle aria-hidden="true" className="animate-spin" /> : null}
            {confirmLabel}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
