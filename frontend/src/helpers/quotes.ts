import { QUOTED_LINE_PATTERN } from '@/consts'

export function extractQuotedLines(idea: string): string[] {
  return [...idea.matchAll(QUOTED_LINE_PATTERN)].map((match) => (match[1] ?? match[2] ?? '').trim()).filter(Boolean)
}
