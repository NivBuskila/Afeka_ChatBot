// ***********************************************************
// This example support/component.js is processed and
// loaded automatically before your component test files.
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

// Import commands for component testing
import './commands'

// Import component testing specific commands
import { mount } from 'cypress/react'

// Augment the Cypress namespace to include type definitions for
// your custom command.
declare global {
  namespace Cypress {
    interface Chainable {
      mount: typeof mount
    }
  }
}

Cypress.Commands.add('mount', mount)

// Component testing setup
beforeEach(() => {
  // Reset any global state before each component test
  cy.window().then((win) => {
    win.localStorage.clear()
    win.sessionStorage.clear()
  })
})

// Global error handling for component tests
Cypress.on('uncaught:exception', (err, runnable) => {
  // Don't fail tests on these common component testing errors
  if (
    err.message.includes('ResizeObserver') ||
    err.message.includes('Non-Error promise rejection captured')
  ) {
    return false
  }
  
  return true
}) 