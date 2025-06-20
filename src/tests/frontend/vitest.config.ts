import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./unit-integration/setup.ts'],
    include: ['./unit-integration/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/e2e/**',
      '**/.{idea,git,cache,output,temp}/**'
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'coverage/**',
        'dist/**',
        '**/node_modules/**',
        '**/*.d.ts',
        '**/*.config.*'
      ],
      thresholds: {
        global: {
          branches: 70,
          functions: 70,
          lines: 70,
          statements: 70
        }
      }
    }
  },
  resolve: {
    alias: {
      // Point to the actual frontend src directory
      '@': path.resolve(__dirname, '../../frontend/src'),
      '@/tests': path.resolve(__dirname, './unit-integration'),
      // Add these additional aliases to help resolve imports
      '@/components': path.resolve(__dirname, '../../frontend/src/components'),
      '@/services': path.resolve(__dirname, '../../frontend/src/services'),
      '@/contexts': path.resolve(__dirname, '../../frontend/src/contexts'),
      '@/hooks': path.resolve(__dirname, '../../frontend/src/hooks'),
      '@/utils': path.resolve(__dirname, '../../frontend/src/utils'),
      '@/types': path.resolve(__dirname, '../../frontend/src/types'),
      '@/config': path.resolve(__dirname, '../../frontend/src/config'),
      // Add fallback for relative imports
      '../../src': path.resolve(__dirname, '../../frontend/src'),
      '../../../src': path.resolve(__dirname, '../../frontend/src')
    }
  }
})