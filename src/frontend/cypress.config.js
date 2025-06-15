import { defineConfig } from 'cypress'

export default defineConfig({
  // Viewport settings
  viewportWidth: 1280,
  viewportHeight: 720,
  
  // Test files path
  e2e: {
    baseUrl: 'http://localhost:5173',
    specPattern: 'cypress/e2e/**/*.cy.js',
    supportFile: false,
    setupNodeEvents(on, config) {
      // implement node event listeners here if needed
    },
  },

  // Video recording (disabled for CI/CD to save resources)
  video: false,
  
  // Default timeout for commands
  defaultCommandTimeout: 5000,
  
  // Skip retrying failing tests
  retries: {
    runMode: 0,
    openMode: 0,
  },
}) 