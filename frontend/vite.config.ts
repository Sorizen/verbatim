import { fileURLToPath, URL } from 'node:url'

import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const API_TARGET = 'http://localhost:8010'
const DEV_PORT = 5173

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  server: {
    port: DEV_PORT,
    proxy: { '/api': API_TARGET },
  },
})
