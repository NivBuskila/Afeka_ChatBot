import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Use env vars to check if we should skip TypeScript checks
const skipTypeCheck = process.env.VITE_SKIP_TS_CHECK === 'true'

export default defineConfig({
  plugins: [react()],
  // Disable type checking in build process when indicated
  build: {
    // Skip type checking when env var is set
    typescript: {
      ignoreBuildErrors: skipTypeCheck
    }
  },
  server: {
    // Allow connections from outside
    host: '0.0.0.0',
    // Accept connections on any network interface
    cors: true,
    // Add proxy configuration for API requests
    proxy: {
      '/api/chat': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/chat/, '/chat')
      }
    }
  }
})