import { useTranslation } from 'react-i18next'

import { useReviewRun } from '@/hooks'

import styles from './ReviewBar.module.scss'

const TITLE_ID = 'review-title'

interface ReviewBarProps {
  runId: string
  reason: string | null
}

export function ReviewBar({ runId, reason }: ReviewBarProps) {
  const { t } = useTranslation()
  const review = useReviewRun(runId)
  return (
    <section className={styles['review-bar']} aria-labelledby={TITLE_ID}>
      <h2 id={TITLE_ID} className={styles['review-bar__title']}>
        {t('review.title')}
      </h2>
      {reason && <p className={styles['review-bar__reason']}>{reason}</p>}
      <div className={styles['review-bar__actions']}>
        <button
          type="button"
          className={styles['review-bar__accept']}
          disabled={review.isPending}
          onClick={() => {
            review.mutate(true)
          }}
        >
          {review.isPending ? t('review.sending') : t('review.accept')}
        </button>
        <button
          type="button"
          className={styles['review-bar__reject']}
          disabled={review.isPending}
          onClick={() => {
            review.mutate(false)
          }}
        >
          {t('review.reject')}
        </button>
      </div>
    </section>
  )
}
