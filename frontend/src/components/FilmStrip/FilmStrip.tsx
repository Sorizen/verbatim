import { useTranslation } from 'react-i18next'

import type { StripFrame } from '@/types'

import { FilmFrame } from './FilmFrame'
import styles from './FilmStrip.module.scss'

interface FilmStripProps {
  frames: StripFrame[]
}

export function FilmStrip({ frames }: FilmStripProps) {
  const { t } = useTranslation()
  return (
    <ol className={styles['film-strip']} aria-label={t('frame.strip-label')}>
      {frames.map((frame) => (
        <FilmFrame key={frame.key} frame={frame} />
      ))}
    </ol>
  )
}
