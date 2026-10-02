import { useTranslation } from 'react-i18next'
import { useParams } from 'react-router'

import { FilmStrip } from '@/components/FilmStrip'
import { LinesPanel } from '@/components/LinesPanel'
import { Monitor } from '@/components/Monitor'
import { RecoveryBar } from '@/components/RecoveryBar'
import { ReviewBar } from '@/components/ReviewBar'
import { RUN_STATUS } from '@/consts'
import { buildStripFrames, formatCost, isAccepted } from '@/helpers'
import { useRun, useRunLines } from '@/hooks'

import styles from './RunPage.module.scss'
import { RunSlate } from './RunSlate'

const NOT_FOUND_STATUS = 404

export function RunPage() {
  const { t } = useTranslation()
  const { runId = '' } = useParams()
  const runQuery = useRun(runId)
  const run = runQuery.data
  const lines = useRunLines(runId, run?.steps.length ?? 0)

  if (runQuery.isError) {
    const missing = 'status' in runQuery.error && runQuery.error.status === NOT_FOUND_STATUS
    return (
      <main className={styles['run-page']}>
        <p role="alert" className={styles['run-page__error']}>
          {missing ? t('errors.missing') : t('errors.load')}
        </p>
      </main>
    )
  }
  if (!run) return <main className={styles['run-page']} aria-busy="true" />

  return (
    <main className={styles['run-page']}>
      <aside className={styles['run-page__monitor']}>
        <Monitor videoUrl={run.video_url ?? null} label={t('monitor.label')}>
          <RunSlate run={run} />
        </Monitor>
      </aside>
      <div className={styles['run-page__body']}>
        <p className={styles['run-page__idea']}>{run.idea}</p>
        <p className={styles['run-page__status']}>
          {isAccepted(run) ? t('status.accepted') : t(`status.${run.status}`)}
          <span className={styles['run-page__cost']}>{t('meta.cost', { cost: formatCost(run.cost_usd) })}</span>
        </p>
        <FilmStrip frames={buildStripFrames(run.steps, run.status)} />
        {run.status === RUN_STATUS.NEEDS_REVIEW && <ReviewBar runId={run.id} reason={run.review_reason} />}
        {run.status === RUN_STATUS.FAILED && <RecoveryBar run={run} />}
        <LinesPanel lines={lines.data ?? []} />
      </div>
    </main>
  )
}
