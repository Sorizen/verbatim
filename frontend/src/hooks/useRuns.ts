import { useQuery } from '@tanstack/react-query'

import { fetchRuns } from '@/api/runs'
import { RECENT_RUNS_LIMIT } from '@/consts'
import { QueryKey } from '@/enums'

export function useRuns() {
  return useQuery({
    queryKey: [QueryKey.Runs],
    queryFn: () => fetchRuns(RECENT_RUNS_LIMIT),
  })
}
