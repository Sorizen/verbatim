import { FINISHED_STATUSES, FIRST_ATTEMPT, STEP, STEP_SEQUENCE } from '@/consts'
import { FrameState } from '@/enums'
import type { RunStatus, RunStep, StepName, StepStatus, StripFrame } from '@/types'

const PENDING_KEY_PREFIX = 'pending-'
const FRAME_STATES: Record<StepStatus, FrameState> = {
  running: FrameState.Running,
  ok: FrameState.Ok,
  rejected: FrameState.Rejected,
  failed: FrameState.Failed,
}

function toFrame(step: RunStep): StripFrame {
  return {
    key: step.id,
    step: step.name,
    attempt: step.attempt,
    state: FRAME_STATES[step.status],
    detail: step.detail,
  }
}

function upcomingSteps(steps: RunStep[], status: RunStatus): StepName[] {
  if (FINISHED_STATUSES.has(status)) return []
  const last = steps.at(-1)
  if (!last) return [...STEP_SEQUENCE]
  if (last.name === STEP.SHOT_FIX) return STEP_SEQUENCE.slice(STEP_SEQUENCE.indexOf(STEP.RENDER))
  return STEP_SEQUENCE.slice(STEP_SEQUENCE.indexOf(last.name) + 1)
}

export function buildStripFrames(steps: RunStep[], status: RunStatus): StripFrame[] {
  const pending = upcomingSteps(steps, status).map((step) => ({
    key: `${PENDING_KEY_PREFIX}${step}`,
    step,
    attempt: FIRST_ATTEMPT,
    state: FrameState.Pending,
    detail: null,
  }))
  return [...steps.map(toFrame), ...pending]
}
