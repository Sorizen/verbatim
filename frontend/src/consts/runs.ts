import type { RunStatus, StepName } from '@/types'

export const RECENT_RUNS_LIMIT = 6
export const IDEA_EXCERPT_LENGTH = 90
export const COST_FRACTION_DIGITS = 2
export const FIRST_ATTEMPT = 1

export const RUN_STATUS = {
  QUEUED: 'queued',
  RUNNING: 'running',
  DONE: 'done',
  NEEDS_REVIEW: 'needs_review',
  FAILED: 'failed',
} as const satisfies Record<string, RunStatus>

export const STEP = {
  BRIEF: 'brief',
  SCRIPT: 'script',
  SCRIPT_CHECK: 'script_check',
  CAST: 'cast',
  PORTRAITS: 'portraits',
  PORTRAIT_CHECK: 'portrait_check',
  SCENE: 'scene',
  RENDER: 'render',
  SCENE_CHECK: 'scene_check',
  SHOT_FIX: 'shot_fix',
  FINAL: 'final',
} as const satisfies Record<string, StepName>

export const STEP_SEQUENCE: readonly StepName[] = [
  STEP.BRIEF,
  STEP.SCRIPT,
  STEP.SCRIPT_CHECK,
  STEP.CAST,
  STEP.PORTRAITS,
  STEP.PORTRAIT_CHECK,
  STEP.SCENE,
  STEP.RENDER,
  STEP.SCENE_CHECK,
  STEP.FINAL,
]

export const SETTLED_STATUSES: ReadonlySet<RunStatus> = new Set<RunStatus>([
  RUN_STATUS.DONE,
  RUN_STATUS.FAILED,
  RUN_STATUS.NEEDS_REVIEW,
])

export const FINISHED_STATUSES: ReadonlySet<RunStatus> = new Set<RunStatus>([RUN_STATUS.DONE, RUN_STATUS.FAILED])
