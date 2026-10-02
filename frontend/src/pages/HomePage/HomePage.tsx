import { useTranslation } from 'react-i18next'

import { IdeaForm } from '@/components/IdeaForm'
import { Monitor, MonitorSlate } from '@/components/Monitor'
import { RecentRuns } from '@/components/RecentRuns'
import { RUN_STATUS } from '@/consts'
import { useRuns } from '@/hooks'

import styles from './HomePage.module.scss'

export function HomePage() {
  const { t } = useTranslation()
  const runs = useRuns()
  const recent = runs.data ?? []
  const latest = recent.find((run) => run.status === RUN_STATUS.DONE && run.video_url)
  return (
    <main className={styles['home-page']}>
      <div className={styles['home-page__stage']}>
        <div className={styles['home-page__script']}>
          <IdeaForm />
        </div>
        <div className={styles['home-page__monitor']}>
          <Monitor videoUrl={latest?.video_url ?? null} label={t('monitor.label')} ambient>
            <MonitorSlate title={t('monitor.empty')} />
          </Monitor>
        </div>
        {recent.length > 0 && (
          <div className={styles['home-page__runs']}>
            <RecentRuns runs={recent} />
          </div>
        )}
      </div>
    </main>
  )
}
