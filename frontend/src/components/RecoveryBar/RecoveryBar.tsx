import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router'

import { runPath } from '@/helpers'
import { useContinueRun, useCreateRun } from '@/hooks'
import type { Run } from '@/types'

import styles from './RecoveryBar.module.scss'

const TITLE_ID = 'recovery-title'

interface RecoveryBarProps {
  run: Run
}

export function RecoveryBar({ run }: RecoveryBarProps) {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const continueRun = useContinueRun(run.id)
  const createRun = useCreateRun()
  const busy = continueRun.isPending || createRun.isPending
  const failure = continueRun.error ?? createRun.error
  const continueLabel = run.current_step
    ? t('recovery.continue-from', { step: t(`step.${run.current_step}`) })
    : t('recovery.continue')

  const startOver = () => {
    createRun.mutate(run.idea, {
      onSuccess: (created) => {
        void navigate(runPath(created.id))
      },
    })
  }

  return (
    <section className={styles['recovery-bar']} aria-labelledby={TITLE_ID}>
      <h2 id={TITLE_ID} className={styles['recovery-bar__title']}>
        {t('recovery.title')}
      </h2>
      <p role="alert" className={styles['recovery-bar__reason']}>
        {run.error ?? run.review_reason}
      </p>
      <div className={styles['recovery-bar__actions']}>
        {run.can_continue && (
          <button
            type="button"
            className={styles['recovery-bar__main']}
            disabled={busy}
            onClick={() => {
              continueRun.mutate()
            }}
          >
            {continueRun.isPending ? t('recovery.sending') : continueLabel}
          </button>
        )}
        <button
          type="button"
          className={run.can_continue ? styles['recovery-bar__other'] : styles['recovery-bar__main']}
          disabled={busy}
          onClick={startOver}
        >
          {createRun.isPending ? t('recovery.sending') : t('recovery.start-over')}
        </button>
      </div>
      {failure && (
        <p role="alert" className={styles['recovery-bar__error']}>
          {t('recovery.error', { message: failure.message })}
        </p>
      )}
    </section>
  )
}
