import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    // You only need proxy settings here if you want to avoid 
    // writing 'http://localhost:8000' in your api.js baseURL.
  }
})