import clsx from 'clsx'
import { useTranslation } from 'react-i18next'

import { FIRST_ATTEMPT } from '@/consts'
import { FrameState } from '@/enums'
import type { StripFrame } from '@/types'

import styles from './FilmFrame.module.scss'

interface FilmFrameProps {
  frame: StripFrame
}

export function FilmFrame({ frame }: FilmFrameProps) {
  const { t } = useTranslation()
  const isPending = frame.state === FrameState.Pending
  return (
    <li className={clsx(styles['film-frame'], styles[`film-frame--${frame.state}`])} title={frame.detail ?? undefined}>
      <span className={clsx(styles['film-frame__step'], isPending && styles['film-frame__step--pending'])}>
        {t(`step.${frame.step}`)}
      </span>
      <span className={styles['film-frame__meta']}>
        {frame.attempt > FIRST_ATTEMPT && (
          <span className={styles['film-frame__attempt']}>{t('frame.attempt', { attempt: frame.attempt })}</span>
        )}
        <span className={clsx(styles['film-frame__state'], styles[`film-frame__state--${frame.state}`])}>
          {t(`frame.${frame.state}`)}
        </span>
      </span>
      {frame.state === FrameState.Running && <span className={styles['film-frame__progress']} aria-hidden="true" />}
    </li>
  )
}
