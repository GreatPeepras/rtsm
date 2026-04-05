import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      // RTSM API (objects overlay)
      '/api': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api/, '')
      },
      // Demo server WebSocket (point cloud streaming)
      '/ws': {
        target: 'ws://localhost:8083',
        ws: true,
        changeOrigin: true
      }
    }
  }
})

