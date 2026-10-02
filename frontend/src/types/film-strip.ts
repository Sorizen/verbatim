import type { FrameState } from '@/enums'
import type { StepName } from './api'

export interface StripFrame {
  key: string
  step: StepName
  attempt: number
  state: FrameState
  detail: string | null
}
