import { useTranslation } from 'react-i18next'

import { MonitorSlate } from '@/components/Monitor'
import { RUN_STATUS } from '@/consts'
import { currentTake } from '@/helpers'
import type { Run } from '@/types'

interface RunSlateProps {
  run: Run
}

export function RunSlate({ run }: RunSlateProps) {
  const { t } = useTranslation()
  if (run.status === RUN_STATUS.QUEUED) return <MonitorSlate title={t('monitor.queued')} />
  if (run.status === RUN_STATUS.FAILED) return <MonitorSlate title={t('monitor.failed')} />
  const step = run.current_step ? t(`step.${run.current_step}`) : t(`status.${run.status}`)
  return (
    <MonitorSlate
      take={t('monitor.take', { number: currentTake(run) })}
      title={step}
      caption={t(`status.${run.status}`)}
    />
  )
}
