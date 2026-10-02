import { useTranslation } from 'react-i18next'

import type { RunSummary } from '@/types'

import styles from './RecentRuns.module.scss'
import { RunThumb } from './RunThumb'

const TITLE_ID = 'recent-runs-title'

interface RecentRunsProps {
  runs: RunSummary[]
}

export function RecentRuns({ runs }: RecentRunsProps) {
  const { t } = useTranslation()
  return (
    <section className={styles['recent-runs']} aria-labelledby={TITLE_ID}>
      <h2 id={TITLE_ID} className={styles['recent-runs__title']}>
        {t('runs.title')}
      </h2>
      <ul className={styles['recent-runs__list']}>
        {runs.map((run) => (
          <RunThumb key={run.id} run={run} />
        ))}
      </ul>
    </section>
  )
}
