import clsx from 'clsx'
import { useTranslation } from 'react-i18next'

import type { LineReport } from '@/types'

import { AlignedWords } from './AlignedWords'
import styles from './LineReportItem.module.scss'

function LineVerdict({ line }: { line: LineReport }) {
  const { t } = useTranslation()
  const mismatches = line.diff.length
  return (
    <div className={styles['line-report__verdict']}>
      <p className={styles['line-report__heard-label']}>{t('lines.heard', { attempt: line.attempt })}</p>
      <AlignedWords words={line.alignment} />
      <p className={styles['line-report__summary']}>
        <span
          className={clsx(
            styles['line-report__mark'],
            mismatches ? styles['line-report__mark--bad'] : styles['line-report__mark--ok'],
          )}
        >
          {mismatches ? t('lines.mismatches', { count: mismatches }) : t('lines.word-perfect')}
        </span>
        {line.speaker_matches !== null && (
          <span
            className={clsx(
              styles['line-report__mark'],
              line.speaker_matches ? styles['line-report__mark--ok'] : styles['line-report__mark--bad'],
            )}
          >
            {line.speaker_matches
              ? t('lines.speaker-ok', { name: line.speaker_name })
              : t('lines.speaker-bad', { name: line.speaker_name })}
          </span>
        )}
      </p>
    </div>
  )
}

interface LineReportItemProps {
  line: LineReport
}

export function LineReportItem({ line }: LineReportItemProps) {
  const { t } = useTranslation()
  return (
    <li className={styles['line-report']}>
      <p className={styles['line-report__head']}>
        <span className={styles['line-report__speaker']}>{line.speaker_name}</span>
        {line.locked && <span className={styles['line-report__locked']}>{t('lines.locked')}</span>}
      </p>
      <p className={styles['line-report__text']}>{line.text}</p>
      {line.attempt ? (
        <LineVerdict line={line} />
      ) : (
        <p className={styles['line-report__pending']}>{t('lines.not-checked')}</p>
      )}
    </li>
  )
}
