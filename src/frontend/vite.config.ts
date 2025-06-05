import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  // ✅ FIXED: Correct path back to project root (src/frontend -> Apex/Afeka_ChatBot)
  const env = loadEnv(mode, '../../', '')  // Back to original working path
  
  // Use env vars to check if we should skip TypeScript checks
  const skipTypeCheck = process.env.VITE_SKIP_TS_CHECK === 'true'

  return {
    plugins: [react()],
    
    // ✅ FIXED: Use original variable names that actually get loaded
    define: {
      'import.meta.env.VITE_SUPABASE_URL': JSON.stringify(env.SUPABASE_URL),           // Not env.VITE_SUPABASE_URL
      'import.meta.env.VITE_SUPABASE_ANON_KEY': JSON.stringify(env.SUPABASE_ANON_KEY), // Not env.VITE_SUPABASE_ANON_KEY
    },
    
    // Build configuration
    build: {
      typescript: {
        ignoreBuildErrors: skipTypeCheck
      }
    },
    
    server: {
      host: '0.0.0.0',
      cors: true,
      // Proxy API requests to backend (port 8000)
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          configure: (proxy, _options) => {
            proxy.on('error', (err, _req, _res) => {
              console.log('Proxy error:', err);
            });
            proxy.on('proxyReq', (proxyReq, req, _res) => {
              console.log('Sending Request to the Target:', req.method, req.url);
            });
            proxy.on('proxyRes', (proxyRes, req, _res) => {
              console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
            });
          },
        }
      }
    }
  }
})