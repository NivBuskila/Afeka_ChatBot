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
      // Proxy all requests starting with /api to the backend server
      '/api': { 
        target: 'http://localhost:8000', // Target our main backend server
        changeOrigin: true,
        // No rewrite needed if backend handles /api/chat, /api/documents, etc.
        // If backend expects /chat, /documents, then use:
        // rewrite: (path) => path.replace(/^\/api/, '') 
      }
    }
  }
})