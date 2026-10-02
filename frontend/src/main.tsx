import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import '@fontsource/courier-prime/400.css'
import '@fontsource/courier-prime/700.css'
import '@/i18n'
import '@/styles/global.scss'

import { App } from './App'

const ROOT_ELEMENT_ID = 'root'

const container = document.getElementById(ROOT_ELEMENT_ID)
if (container) {
  createRoot(container).render(
    <StrictMode>
      <App />
    </StrictMode>,
  )
}
