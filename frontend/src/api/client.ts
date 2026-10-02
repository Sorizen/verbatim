import { API_PREFIX, JSON_CONTENT_TYPE } from '@/consts'

interface ErrorBody {
  detail?: unknown
}

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as ErrorBody
    const detail = body.detail
    if (Array.isArray(detail)) return JSON.stringify(detail)
    const message = detail as string | undefined
    return message?.length ? message : response.statusText
  } catch {
    return response.statusText
  }
}

export async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_PREFIX}${path}`, init)
  if (!response.ok) throw new ApiError(response.status, await readErrorMessage(response))
  return (await response.json()) as T
}

export function postJson<T>(path: string, body: unknown): Promise<T> {
  return requestJson<T>(path, {
    method: 'POST',
    headers: { 'Content-Type': JSON_CONTENT_TYPE },
    body: JSON.stringify(body),
  })
}
