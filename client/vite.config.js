import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // se já não estiver
    proxy: {
      '/api': {
        target: 'http://10.85.198.140:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
