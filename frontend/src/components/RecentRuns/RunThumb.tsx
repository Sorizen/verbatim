import { useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router'

import { excerpt, runPath } from '@/helpers'
import type { RunSummary } from '@/types'

import styles from './RunThumb.module.scss'

const PREVIEW_START_SECONDS = 0

interface RunThumbProps {
  run: RunSummary
}

export function RunThumb({ run }: RunThumbProps) {
  const { t } = useTranslation()
  const videoRef = useRef<HTMLVideoElement>(null)

  function startPreview() {
    videoRef.current?.play().catch((error: unknown) => {
      console.error('Preview could not start', error)
    })
  }

  function stopPreview() {
    const video = videoRef.current
    if (!video) return
    video.pause()
    video.currentTime = PREVIEW_START_SECONDS
  }

  return (
    <li className={styles['run-thumb']}>
      <Link
        to={runPath(run.id)}
        className={styles['run-thumb__link']}
        title={run.idea}
        onMouseEnter={startPreview}
        onMouseLeave={stopPreview}
      >
        <span className={styles['run-thumb__screen']}>
          {run.video_url && (
            <video
              ref={videoRef}
              className={styles['run-thumb__video']}
              src={run.video_url}
              muted
              playsInline
              loop
              preload="metadata"
            />
          )}
        </span>
        <span className={styles['run-thumb__text']}>
          <span className={styles['run-thumb__status']}>{t(`status.${run.status}`)}</span>
          <span className={styles['run-thumb__idea']}>{excerpt(run.idea)}</span>
        </span>
      </Link>
    </li>
  )
}
