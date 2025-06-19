// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

// General utility commands

// Command to setup common API interceptors
Cypress.Commands.add('setupCommonInterceptors', () => {
  // Intercept authentication requests
  cy.intercept('POST', '**/auth/login', { fixture: 'auth/login-success.json' }).as('login')
  cy.intercept('POST', '**/auth/logout', { statusCode: 200 }).as('logout')
  cy.intercept('GET', '**/auth/user', { fixture: 'auth/user-profile.json' }).as('userProfile')
  
  // Intercept chat requests
  cy.intercept('POST', '**/chat/sessions', { fixture: 'chat/create-session.json' }).as('createChatSession')
  cy.intercept('GET', '**/chat/sessions', { fixture: 'chat/chat-sessions.json' }).as('getChatSessions')
  cy.intercept('POST', '**/chat/messages', { fixture: 'chat/send-message.json' }).as('sendMessage')
  
  // Intercept document requests
  cy.intercept('GET', '**/documents', { fixture: 'documents/document-list.json' }).as('getDocuments')
  cy.intercept('POST', '**/documents/upload', { fixture: 'documents/upload-success.json' }).as('uploadDocument')
  
  // Intercept analytics requests
  cy.intercept('GET', '**/analytics/**', { fixture: 'analytics/dashboard-data.json' }).as('getAnalytics')
})

// Command to wait for API calls to complete
Cypress.Commands.add('waitForApiCalls', (...aliases) => {
  aliases.forEach(alias => {
    cy.wait(`@${alias}`)
  })
})

// Command to fill a form with data
Cypress.Commands.add('fillForm', (formData) => {
  Object.entries(formData).forEach(([field, value]) => {
    cy.get(`[data-cy="${field}"], [name="${field}"]`).clear().type(value)
  })
})

// Command to check if element is in viewport
Cypress.Commands.add('isInViewport', { prevSubject: true }, (subject) => {
  cy.wrap(subject).should(($el) => {
    const rect = $el[0].getBoundingClientRect()
    expect(rect.top).to.be.at.least(0)
    expect(rect.left).to.be.at.least(0)
    expect(rect.bottom).to.be.at.most(Cypress.config('viewportHeight'))
    expect(rect.right).to.be.at.most(Cypress.config('viewportWidth'))
  })
})

// Command to scroll element into view smoothly - overwriting existing command
Cypress.Commands.overwrite('scrollIntoView', (originalFn, subject, options = {}) => {
  return originalFn(subject, {
    duration: 500,
    easing: 'swing',
    ...options
  })
})

// Command to take a screenshot with timestamp
Cypress.Commands.add('screenshotWithTimestamp', (name) => {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  cy.screenshot(`${name}-${timestamp}`)
})

// Command to check page performance
Cypress.Commands.add('checkPagePerformance', () => {
  cy.window().then(win => {
    cy.wrap(win.performance.timing).should('exist')
    
    // Check load time is reasonable (under 3 seconds)
    const loadTime = win.performance.timing.loadEventEnd - win.performance.timing.navigationStart
    expect(loadTime).to.be.lessThan(3000)
  })
})

// Command to test drag and drop functionality
Cypress.Commands.add('dragAndDrop', (sourceSelector, targetSelector) => {
  cy.get(sourceSelector).trigger('mousedown', { button: 0 })
  cy.get(targetSelector).trigger('mousemove').trigger('mouseup')
})

// Command to test file upload
Cypress.Commands.add('uploadFile', (inputSelector, fileName, fileType = 'text/plain') => {
  cy.fixture(fileName).then(fileContent => {
    cy.get(inputSelector).then(input => {
      const blob = new Blob([fileContent], { type: fileType })
      const file = new File([blob], fileName, { type: fileType })
      
      const dataTransfer = new DataTransfer()
      dataTransfer.items.add(file)
      
      input[0].files = dataTransfer.files
      cy.wrap(input).trigger('change', { force: true })
    })
  })
})

// Command to check if text is visible on screen
Cypress.Commands.add('containsVisible', (text) => {
  cy.contains(text).should('be.visible')
})

// Command to wait for loading to complete
Cypress.Commands.add('waitForLoading', () => {
  cy.get('[data-cy="loading"], .loading, [data-testid="loading"]').should('not.exist')
  cy.get('body').should('not.have.class', 'loading')
})

// Command to clear all storage
Cypress.Commands.add('clearAllStorage', () => {
  cy.clearLocalStorage()
  cy.clearCookies()
  // Clear session storage via window object since cy.clearSessionStorage doesn't exist
  cy.window().then(win => {
    win.sessionStorage.clear()
  })
})

// Command to mock API responses
Cypress.Commands.add('mockApiResponse', (method, url, response, statusCode = 200) => {
  cy.intercept(method, url, {
    statusCode,
    body: response
  })
})

// Command to check responsive breakpoints
Cypress.Commands.add('checkResponsiveBreakpoints', () => {
  const breakpoints = [
    { name: 'mobile', width: 375 },
    { name: 'tablet', width: 768 },
    { name: 'desktop', width: 1024 },
    { name: 'wide', width: 1440 }
  ]
  
  breakpoints.forEach(bp => {
    cy.viewport(bp.width, 800)
    cy.get('[data-cy="main-content"]').should('be.visible')
    cy.log(`✓ ${bp.name} breakpoint (${bp.width}px) working`)
  })
})

// Command to verify meta tags
Cypress.Commands.add('checkMetaTags', (expectedTags) => {
  Object.entries(expectedTags).forEach(([name, content]) => {
    cy.get(`meta[name="${name}"]`).should('have.attr', 'content', content)
  })
})

// Command to check external links
Cypress.Commands.add('checkExternalLinks', () => {
  cy.get('a[href^="http"]').each($link => {
    cy.wrap($link).should('have.attr', 'target', '_blank')
    cy.wrap($link).should('have.attr', 'rel').and('include', 'noopener')
  })
})

// Command to simulate network conditions
Cypress.Commands.add('simulateNetworkConditions', (condition) => {
  const conditions = {
    offline: { online: false },
    slow3g: { downlink: 0.4, rtt: 2000 },
    fast3g: { downlink: 1.6, rtt: 562.5 },
    slow4g: { downlink: 4, rtt: 300 }
  }
  
  if (conditions[condition]) {
    cy.window().then(win => {
      Object.defineProperty(win.navigator, 'connection', {
        value: conditions[condition]
      })
    })
  }
})

// Command to check console errors
Cypress.Commands.add('checkConsoleErrors', () => {
  cy.window().then(win => {
    const errors = []
    const originalError = win.console.error
    
    win.console.error = (...args) => {
      errors.push(args.join(' '))
      originalError.apply(win.console, args)
    }
    
    cy.wrap(null).then(() => {
      expect(errors.length).to.equal(0, `Console errors found: ${errors.join(', ')}`)
    })
  })
})

// Command to simulate tab key navigation
Cypress.Commands.add('tab', { prevSubject: 'element' }, (subject) => {
  cy.wrap(subject).trigger('keydown', { keyCode: 9, key: 'Tab' })
  return cy.focused()
})

// Command to login as a regular user
Cypress.Commands.add('loginAsUser', () => {
  cy.visit('/login')
  cy.waitForApp()
  cy.get('[data-cy="email-input"], input[type="email"], input[name="email"]').should('be.visible').type('test@example.com')
  cy.get('[data-cy="password-input"], input[type="password"], input[name="password"]').should('be.visible').type('testpassword123')
  cy.get('[data-cy="login-button"], button[type="submit"], .login-button').should('be.visible').click()
  
  // Wait for potential redirect
  cy.wait(2000)
})

// Command to login as admin user
Cypress.Commands.add('loginAsAdmin', () => {
  cy.visit('/login')
  cy.waitForApp()
  cy.get('[data-cy="email-input"], input[type="email"], input[name="email"]').should('be.visible').type('admin@example.com')
  cy.get('[data-cy="password-input"], input[type="password"], input[name="password"]').should('be.visible').type('adminpassword123')
  cy.get('[data-cy="login-button"], button[type="submit"], .login-button').should('be.visible').click()
  
  // Wait for potential redirect
  cy.wait(2000)
})

// Command to fill registration form
Cypress.Commands.add('fillRegistrationForm', (email, password, userData = {}) => {
  if (userData.firstName) cy.get('[data-cy="first-name-input"], input[name="firstName"]').type(userData.firstName)
  if (userData.lastName) cy.get('[data-cy="last-name-input"], input[name="lastName"]').type(userData.lastName)
  cy.get('[data-cy="email-input"], input[type="email"], input[name="email"]').type(email)
  cy.get('[data-cy="password-input"], input[type="password"], input[name="password"]').type(password)
})

// Command to verify email (simulated)
Cypress.Commands.add('verifyEmail', (email) => {
  // Simulate email verification process
  cy.log(`Simulating email verification for ${email}`)
  cy.window().then(win => {
    win.localStorage.setItem('emailVerified', 'true')
  })
})

// Command to verify login error
Cypress.Commands.add('verifyLoginError', (expectedMessage) => {
  cy.get('[data-cy="login-error"], .error-message, .alert-error').should('contain', expectedMessage)
})

// Command to reset password
Cypress.Commands.add('resetPassword', (email) => {
  cy.get('[data-cy="forgot-password-link"], .forgot-password').click()
  cy.get('[data-cy="reset-email-input"], input[type="email"]').type(email)
  cy.get('[data-cy="reset-submit"], button[type="submit"]').click()
  cy.get('[data-cy="reset-success"], .success-message').should('be.visible')
})

// Command to verify user is authenticated
Cypress.Commands.add('verifyAuthenticated', () => {
  cy.window().then(win => {
    expect(win.localStorage.getItem('supabase.auth.token')).to.exist
  })
}) 