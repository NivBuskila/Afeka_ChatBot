import { defineConfig } from 'cypress'

export default defineConfig({
  // Viewport settings
  viewportWidth: 1280,
  viewportHeight: 720,
  
  // Test files path
  e2e: {
    baseUrl: 'http://localhost:5173',
    specPattern: 'cypress/e2e/**/*.cy.{js,ts}',
    supportFile: 'cypress/support/e2e.js',
    setupNodeEvents(on, config) {
      // implement node event listeners here if needed
      
      // Add any plugins here
      return config;
    },
    // Environment variables
    env: {
      // Add test environment variables
      TEST_USER_EMAIL: 'test@example.com',
      TEST_USER_PASSWORD: 'testpassword123',
      TEST_ADMIN_EMAIL: 'admin@example.com',
      TEST_ADMIN_PASSWORD: 'adminpassword123'
    }
  },

  // Video recording (enabled for comprehensive testing)
  video: true,
  videosFolder: 'cypress/videos',
  
  // Screenshots
  screenshotOnRunFailure: true,
  screenshotsFolder: 'cypress/screenshots',
  
  // Default timeout for commands
  defaultCommandTimeout: 10000,
  requestTimeout: 15000,
  responseTimeout: 15000,
  
  // Retries for better reliability
  retries: {
    runMode: 2,
    openMode: 0,
  },

  // Component testing configuration
  component: {
    devServer: {
      framework: 'react',
      bundler: 'vite',
    },
    specPattern: 'src/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/component.js'
  },

  // Additional settings for Phase 4
  chromeWebSecurity: false,
  defaultBrowser: 'chrome',
  
  // Mobile testing viewports
  userAgent: 'Mozilla/5.0 (compatible; Cypress)',
  
  // Performance and reliability
  numTestsKeptInMemory: 50,
  watchForFileChanges: false,
  
  // Accessibility testing
  env: {
    ...this?.env,
    coverage: false,
    codeCoverage: {
      exclude: 'cypress/**/*.*'
    }
  }
}) 