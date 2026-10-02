import { COST_FRACTION_DIGITS, IDEA_EXCERPT_LENGTH, RUN_PATH_PREFIX } from '@/consts'

const ELLIPSIS = '…'
const TRAILING_PUNCTUATION = /[\s.,;:!?…]+$/u

export function formatCost(usd: number): string {
  return usd.toFixed(COST_FRACTION_DIGITS)
}

export function excerpt(text: string, length = IDEA_EXCERPT_LENGTH): string {
  if (text.length <= length) return text
  return `${text.slice(0, length).replace(TRAILING_PUNCTUATION, '')}${ELLIPSIS}`
}

export function runPath(runId: string): string {
  return `${RUN_PATH_PREFIX}${runId}`
}
