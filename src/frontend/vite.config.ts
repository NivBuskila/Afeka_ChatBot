import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

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
  resolve: {
    alias: {
      'i18next-http-backend': path.resolve(__dirname, 'node_modules/i18next-http-backend/dist/esm/i18nextHttpBackend.js'),
      'i18next-browser-languagedetector': path.resolve(__dirname, 'node_modules/i18next-browser-languagedetector/dist/esm/i18nextBrowserLanguageDetector.js')
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