import type { components } from '@/api/schema'

type Schemas = components['schemas']

export type Run = Schemas['RunSchema']
export type RunSummary = Schemas['RunSummarySchema']
export type RunStep = Schemas['RunStepSchema']
export type RunStatus = Schemas['RunStatus']
export type StepName = Schemas['StepName']
export type StepStatus = Schemas['StepStatus']
export type LineReport = Schemas['LineReportSchema']
export type AlignedWord = Schemas['AlignedWordSchema']
export type DiffOp = Schemas['DiffOp']
