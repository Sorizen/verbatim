import { useTranslation } from 'react-i18next'
import { Link } from 'react-router'

import { ROUTE_PATHS } from '@/consts'

import styles from './AppHeader.module.scss'

interface AppHeaderProps {
  showNewScene: boolean
}

export function AppHeader({ showNewScene }: AppHeaderProps) {
  const { t } = useTranslation()
  return (
    <header className={styles['app-header']}>
      <Link to={ROUTE_PATHS.HOME} className={styles['app-header__wordmark']}>
        {t('app.name')}
      </Link>
      <p className={styles['app-header__tagline']}>{t('app.tagline')}</p>
      {showNewScene && (
        <Link to={ROUTE_PATHS.HOME} className={styles['app-header__action']}>
          {t('app.new-scene')}
        </Link>
      )}
    </header>
  )
}
