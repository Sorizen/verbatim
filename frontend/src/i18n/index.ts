import i18next from 'i18next'
import { initReactI18next } from 'react-i18next'

import en from '@/locales/en.json'

const DEFAULT_LANGUAGE = 'en'

void i18next.use(initReactI18next).init({
  lng: DEFAULT_LANGUAGE,
  fallbackLng: DEFAULT_LANGUAGE,
  resources: { [DEFAULT_LANGUAGE]: { translation: en } },
  interpolation: { escapeValue: false },
})

export default i18next
