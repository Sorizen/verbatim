import type { ReactNode } from 'react'

import styles from './Monitor.module.scss'

interface MonitorProps {
  videoUrl: string | null
  label: string
  ambient?: boolean
  children: ReactNode
}

export function Monitor({ videoUrl, label, ambient = false, children }: MonitorProps) {
  return (
    <figure className={styles.monitor} aria-label={label}>
      {videoUrl ? (
        <video
          key={videoUrl}
          className={styles.monitor__video}
          src={videoUrl}
          controls
          playsInline
          preload="metadata"
          autoPlay={ambient}
          muted={ambient}
          loop={ambient}
        />
      ) : (
        <div className={styles.monitor__slate}>{children}</div>
      )}
    </figure>
  )
}
