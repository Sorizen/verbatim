import { useQuery } from '@tanstack/react-query'

import { fetchRun } from '@/api/runs'
import { RUN_POLL_INTERVAL_MS } from '@/consts'
import { QueryKey } from '@/enums'
import { isSettled } from '@/helpers'

export function useRun(runId: string) {
  return useQuery({
    queryKey: [QueryKey.Run, runId],
    queryFn: () => fetchRun(runId),
    refetchInterval: (query) => (isSettled(query.state.data?.status) ? false : RUN_POLL_INTERVAL_MS),
  })
}
