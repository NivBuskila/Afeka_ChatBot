// Authentication related commands for Cypress E2E tests

// Command to login as a regular user
Cypress.Commands.add('loginAsUser', (email, password) => {
  const userEmail = email || Cypress.env('TEST_USER_EMAIL')
  const userPassword = password || Cypress.env('TEST_USER_PASSWORD')
  
  cy.session(`user-${userEmail}`, () => {
    cy.visit('/login')
    cy.waitForApp()
    
    // Fill login form
    cy.get('[data-cy="email-input"]').type(userEmail)
    cy.get('[data-cy="password-input"]').type(userPassword)
    cy.get('[data-cy="login-button"]').click()
    
    // Wait for successful login
    cy.url().should('not.include', '/login')
    cy.get('[data-cy="user-menu"]').should('be.visible')
  })
})

// Command to login as an admin user
Cypress.Commands.add('loginAsAdmin', (email, password) => {
  const adminEmail = email || Cypress.env('TEST_ADMIN_EMAIL')
  const adminPassword = password || Cypress.env('TEST_ADMIN_PASSWORD')
  
  cy.session(`admin-${adminEmail}`, () => {
    cy.visit('/login')
    cy.waitForApp()
    
    // Fill login form
    cy.get('[data-cy="email-input"]').type(adminEmail)
    cy.get('[data-cy="password-input"]').type(adminPassword)
    cy.get('[data-cy="login-button"]').click()
    
    // Wait for successful login and admin access
    cy.url().should('not.include', '/login')
    cy.get('[data-cy="admin-menu"]').should('be.visible')
  })
})

// Command to sign up a new user
Cypress.Commands.add('signUpUser', (userData) => {
  const {
    email = `test-${Date.now()}@example.com`,
    password = 'testpassword123',
    firstName = 'Test',
    lastName = 'User'
  } = userData || {}
  
  cy.visit('/signup')
  cy.waitForApp()
  
  // Fill signup form
  cy.get('[data-cy="first-name-input"]').type(firstName)
  cy.get('[data-cy="last-name-input"]').type(lastName)
  cy.get('[data-cy="email-input"]').type(email)
  cy.get('[data-cy="password-input"]').type(password)
  cy.get('[data-cy="confirm-password-input"]').type(password)
  
  // Accept terms if checkbox exists
  cy.get('body').then($body => {
    if ($body.find('[data-cy="terms-checkbox"]').length > 0) {
      cy.get('[data-cy="terms-checkbox"]').check()
    }
  })
  
  cy.get('[data-cy="signup-button"]').click()
  
  return cy.wrap({ email, password, firstName, lastName })
})

// Command to logout current user
Cypress.Commands.add('logout', () => {
  cy.get('[data-cy="user-menu"]').click()
  cy.get('[data-cy="logout-button"]').click()
  cy.url().should('include', '/login')
})

// Command to verify user is authenticated
Cypress.Commands.add('verifyAuthenticated', () => {
  cy.get('[data-cy="user-menu"]').should('be.visible')
  cy.url().should('not.include', '/login')
})

// Command to verify user is not authenticated
Cypress.Commands.add('verifyNotAuthenticated', () => {
  cy.visit('/dashboard')
  cy.url().should('include', '/login')
})

// Command to check if user has admin privileges
Cypress.Commands.add('verifyAdminAccess', () => {
  cy.get('[data-cy="admin-menu"]').should('be.visible')
  cy.visit('/admin')
  cy.url().should('include', '/admin')
  cy.get('[data-cy="admin-dashboard"]').should('be.visible')
})

// Command to simulate email verification (for testing)
Cypress.Commands.add('verifyEmail', (email) => {
  // This would typically involve checking email service or database
  // For testing purposes, we'll simulate the verification
  cy.log(`Simulating email verification for: ${email}`)
  
  // If there's a verification page, interact with it
  cy.get('body').then($body => {
    if ($body.find('[data-cy="email-verification-notice"]').length > 0) {
      cy.get('[data-cy="skip-verification"]').click()
    }
  })
})

// Command to fill registration form
Cypress.Commands.add('fillRegistrationForm', (email, password, additionalData = {}) => {
  const {
    firstName = 'Test',
    lastName = 'User',
    confirmPassword = password
  } = additionalData
  
  cy.get('[data-cy="first-name-input"]').clear().type(firstName)
  cy.get('[data-cy="last-name-input"]').clear().type(lastName)
  cy.get('[data-cy="email-input"]').clear().type(email)
  cy.get('[data-cy="password-input"]').clear().type(password)
  cy.get('[data-cy="confirm-password-input"]').clear().type(confirmPassword)
})

// Command to handle login errors
Cypress.Commands.add('verifyLoginError', (expectedError) => {
  cy.get('[data-cy="login-error"]').should('be.visible')
  if (expectedError) {
    cy.get('[data-cy="login-error"]').should('contain', expectedError)
  }
})

// Command to reset password
Cypress.Commands.add('resetPassword', (email) => {
  cy.visit('/login')
  cy.get('[data-cy="forgot-password-link"]').click()
  cy.get('[data-cy="reset-email-input"]').type(email)
  cy.get('[data-cy="send-reset-button"]').click()
  cy.get('[data-cy="reset-email-sent"]').should('be.visible')
}) 