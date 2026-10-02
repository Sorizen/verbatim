import { useTranslation } from 'react-i18next'

import styles from './LockedLines.module.scss'

interface LockedLinesProps {
  lines: string[]
}

export function LockedLines({ lines }: LockedLinesProps) {
  const { t } = useTranslation()
  if (!lines.length) return null
  return (
    <section className={styles['locked-lines']} aria-live="polite">
      <h2 className={styles['locked-lines__title']}>{t('idea.locked-title')}</h2>
      <ol className={styles['locked-lines__list']}>
        {lines.map((line, index) => (
          <li key={`${String(index)}-${line}`} className={styles['locked-lines__line']}>
            {line}
          </li>
        ))}
      </ol>
    </section>
  )
}
