import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api/buet': {
        target: 'https://regoffice.buet.ac.bd/filetracker/my-php-api/api',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/buet/, ''),
      },
    },
  },
})
