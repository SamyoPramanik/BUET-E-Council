import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api/buet': {
        target: 'https://regoffice.buet.ac.bd/filetracker/my-php-api/api',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/buet/, '')
      }
    }
  }   // ← make sure this closes 'server'
})    // ← and this closes defineConfig