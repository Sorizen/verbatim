import { useMutation, useQueryClient } from '@tanstack/react-query'

import { reviewRun } from '@/api/runs'
import { QueryKey } from '@/enums'

export function useReviewRun(runId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (approve: boolean) => reviewRun(runId, approve),
    onSuccess: (run) => {
      queryClient.setQueryData([QueryKey.Run, runId], run)
    },
  })
}
