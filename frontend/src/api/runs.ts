import type { components } from '@/api/schema'
import type { LineReport, Run, RunSummary } from '@/types'

import { postJson, requestJson } from './client'

type RunListResponse = components['schemas']['RunListResponse']
type RunLinesResponse = components['schemas']['RunLinesResponse']

export async function fetchRuns(limit: number): Promise<RunSummary[]> {
  const response = await requestJson<RunListResponse>(`/runs?limit=${limit}`)
  return response.items
}

export function fetchRun(runId: string): Promise<Run> {
  return requestJson<Run>(`/runs/${runId}`)
}

export async function fetchRunLines(runId: string): Promise<LineReport[]> {
  const response = await requestJson<RunLinesResponse>(`/runs/${runId}/lines`)
  return response.items
}

export function createRun(idea: string): Promise<Run> {
  return postJson<Run>('/runs', { idea })
}

export function reviewRun(runId: string, approve: boolean): Promise<Run> {
  return postJson<Run>(`/runs/${runId}/review`, { approve })
}

export function continueRun(runId: string): Promise<Run> {
  return postJson<Run>(`/runs/${runId}/continue`, {})
}
