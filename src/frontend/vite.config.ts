import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  // Load env vars from the parent directory (.env file)
  const env = loadEnv(mode, '../../', '')
  
  // Use env vars to check if we should skip TypeScript checks
  const skipTypeCheck = process.env.VITE_SKIP_TS_CHECK === 'true'

  return {
    plugins: [react()],
    // Expose specific environment variables to the frontend
    define: {
      'import.meta.env.VITE_SUPABASE_URL': JSON.stringify(env.SUPABASE_URL),
      'import.meta.env.VITE_SUPABASE_ANON_KEY': JSON.stringify(env.SUPABASE_ANON_KEY),
    },
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
        '/api': {
          target: 'http://localhost:5000',
          changeOrigin: true,
          secure: false
        },
        '/chat': {
          target: 'http://localhost:5000',
          changeOrigin: true
        }
      }
    }
  }
})