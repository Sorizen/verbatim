import { useMutation, useQueryClient } from '@tanstack/react-query'

import { createRun } from '@/api/runs'
import { QueryKey } from '@/enums'

export function useCreateRun() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createRun,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [QueryKey.Runs] }),
  })
}
