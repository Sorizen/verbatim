import { useQuery } from '@tanstack/react-query'

import { fetchRunLines } from '@/api/runs'
import { QueryKey } from '@/enums'

export function useRunLines(runId: string, revision: number) {
  return useQuery({
    queryKey: [QueryKey.RunLines, runId, revision],
    queryFn: () => fetchRunLines(runId),
    placeholderData: (previous) => previous,
  })
}
