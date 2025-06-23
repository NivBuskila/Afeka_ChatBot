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
    },
    // ⚡ Performance Optimizations
    rollupOptions: {
      output: {
        // Bundle splitting for better caching
        manualChunks: {
          // React core
          'react-vendor': ['react', 'react-dom'],
          // UI libraries
          'ui-vendor': ['lucide-react', 'react-i18next', 'lodash']
        }
      }
    },
    // Optimize chunk size
    chunkSizeWarningLimit: 1000,
    // Enable compression
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.logs in production
        drop_debugger: true
      }
    }
  },
  server: {
    // Allow connections from outside
    host: '0.0.0.0',
    // Accept connections on any network interface
    cors: true,
    // ⚡ Development optimizations
    hmr: {
      overlay: false // Disable error overlay for better UX
    },
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
  },
  // ⚡ Optimize dependencies
  optimizeDeps: {
    include: ['react', 'react-dom', 'lucide-react', 'react-i18next'],
    // Force pre-bundling of these dependencies
    force: process.env.NODE_ENV === 'development'
  }
})