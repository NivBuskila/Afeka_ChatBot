// ***********************************************************
// This example support/e2e.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands'
import './auth-commands'
import './selectors'

// Accessibility testing removed

// Alternatively you can use CommonJS syntax:
// require('./commands')

// Global error handling
Cypress.on('uncaught:exception', (err, runnable) => {
  // Returning false here prevents Cypress from failing the test
  // on uncaught exceptions. We'll handle specific exceptions we care about
  console.warn('Uncaught exception:', err.message)
  
  // Don't fail tests on these common non-critical errors
  if (
    err.message.includes('ResizeObserver') ||
    err.message.includes('Non-Error promise rejection captured') ||
    err.message.includes('ChunkLoadError')
  ) {
    return false
  }
  
  // Fail on other exceptions
  return true
})

// Global before hook for all tests
beforeEach(() => {
  // Clear localStorage and sessionStorage before each test
  cy.clearLocalStorage()
  cy.clearCookies()
  
  // Set up common interceptors
  cy.setupCommonInterceptors()
  
  // Setup interceptors and basic configuration
})

// Global after hook
afterEach(() => {
  // Take screenshot on failure
  if (cy.state('test').state === 'failed') {
    cy.screenshot(`failed-${Cypress.spec.name}-${cy.state('test').title}`)
  }
})

// Custom viewport sizes for responsive testing
Cypress.Commands.add('setViewportSize', (size) => {
  const sizes = {
    mobile: [375, 667],
    tablet: [768, 1024],
    desktop: [1280, 720],
    widescreen: [1920, 1080]
  }
  
  if (sizes[size]) {
    cy.viewport(sizes[size][0], sizes[size][1])
  } else {
    throw new Error(`Unknown viewport size: ${size}`)
  }
})

// Wait for application to be ready
Cypress.Commands.add('waitForApp', () => {
  // Wait for body to be visible
  cy.get('body').should('be.visible')
  
  // Wait for loading to disappear if it exists
  cy.get('body').then($body => {
    if ($body.find('[data-cy="loading-screen"]').length > 0) {
      cy.get('[data-cy="loading-screen"]').should('not.exist')
    }
  })
  
  // Route-specific element detection
  cy.url().then(url => {
    if (url.includes('/chat')) {
      // Chat page - wait for chat elements
      cy.get('[data-testid="chat-container"], [data-testid="chat-input"]', { timeout: 10000 }).should('exist')
    } else if (url.includes('/login')) {
      // Login page - wait for login form elements
      cy.get('input[type="email"], input[name="email"], [data-cy="email-input"], form', { timeout: 10000 }).should('exist')
    } else {
      // Other pages - wait for any main content
      cy.get('main, .app-container, form, [data-testid="chat-container"], body > div', { timeout: 10000 }).should('exist')
    }
  })
}) 