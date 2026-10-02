import { useTranslation } from 'react-i18next'

import type { LineReport } from '@/types'

import { LineReportItem } from './LineReportItem'
import styles from './LinesPanel.module.scss'

const TITLE_ID = 'lines-title'

interface LinesPanelProps {
  lines: LineReport[]
}

export function LinesPanel({ lines }: LinesPanelProps) {
  const { t } = useTranslation()
  return (
    <section className={styles['lines-panel']} aria-labelledby={TITLE_ID}>
      <h2 id={TITLE_ID} className={styles['lines-panel__title']}>
        {t('lines.title')}
      </h2>
      {lines.length ? (
        <ol className={styles['lines-panel__list']}>
          {lines.map((line) => (
            <LineReportItem key={line.shot_id} line={line} />
          ))}
        </ol>
      ) : (
        <p className={styles['lines-panel__empty']}>{t('lines.empty')}</p>
      )}
    </section>
  )
}
