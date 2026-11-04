import { PageHeader } from '@/components/ui/page-header'
import { EmptyState } from '@/components/ui/async-state'

type ModulePageProps = {
  title: string
  description: string
}

export function ModulePage({ title, description }: ModulePageProps) {
  return (
    <>
      <PageHeader title={title} description={description} />
      <EmptyState
        description="This shared page layout is ready. Live records and module workflows will be added in later implementation phases."
        title={`${title} workspace`}
      />
    </>
  )
}
