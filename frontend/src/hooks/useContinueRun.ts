import { useMutation, useQueryClient } from '@tanstack/react-query'

import { continueRun } from '@/api/runs'
import { QueryKey } from '@/enums'

export function useContinueRun(runId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => continueRun(runId),
    onSuccess: (run) => {
      queryClient.setQueryData([QueryKey.Run, runId], run)
    },
  })
}
