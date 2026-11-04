import { Badge } from '@/components/ui/badge'

export function StatusBadge({ status }: { status: string }) {
  const variant = status === 'active' ? 'default' : status === 'inactive' ? 'secondary' : 'outline'
  return <Badge variant={variant}>{status.replaceAll('_', ' ')}</Badge>
}
