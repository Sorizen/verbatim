import { RUN_STATUS, SETTLED_STATUSES, STEP } from '@/consts'
import type { Run, RunStatus } from '@/types'

export function isSettled(status: RunStatus | undefined): boolean {
  return Boolean(status && SETTLED_STATUSES.has(status))
}

export function currentTake(run: Run): number {
  const renders = run.steps.filter((step) => step.name === STEP.RENDER)
  return renders.at(-1)?.attempt ?? 1
}

export function isAccepted(run: Run): boolean {
  return run.status === RUN_STATUS.DONE && Boolean(run.review_reason)
}
