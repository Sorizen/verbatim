import styles from './MonitorSlate.module.scss'

interface MonitorSlateProps {
  title: string
  take?: string
  caption?: string
}

export function MonitorSlate({ title, take, caption }: MonitorSlateProps) {
  return (
    <div className={styles['monitor-slate']}>
      {take && (
        <span key={take} className={styles['monitor-slate__take']}>
          {take}
        </span>
      )}
      <p className={styles['monitor-slate__title']}>{title}</p>
      {caption && <p className={styles['monitor-slate__caption']}>{caption}</p>}
    </div>
  )
}
