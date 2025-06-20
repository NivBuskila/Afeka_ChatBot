// Selector mapping for Cypress tests
// Maps expected test selectors to actual application elements

export const selectors = {
  // Authentication selectors
  'email-input': '[name="email"], input[type="email"], [data-cy="email-input"]',
  'password-input': '[name="password"], input[type="password"], [data-cy="password-input"]', 
  'login-button': 'button[type="submit"], .login-button, [data-cy="login-button"]',
  'signup-button': 'button[type="submit"], .signup-button, [data-cy="signup-button"]',
  'logout-button': '.logout-button, [data-cy="logout-button"]',
  
  // Chat selectors (these exist)
  'chat-input': '[data-testid="chat-input"]',
  'send-button': '[data-testid="send-button"]',
  'chat-container': '[data-testid="chat-container"]',
  'chat-history': '[data-testid="chat-history"]',
  'chat-messages': '[data-testid="chat-messages"], .chat-messages',
  
  // Navigation selectors
  'login-link': 'a[href*="login"], .login-link, [data-cy="login-link"]',
  'signup-link': 'a[href*="signup"], .signup-link, [data-cy="signup-link"]',
  'chat-link': 'a[href*="chat"], .chat-link, [data-cy="chat-link"]',
  
  // Form selectors
  'first-name-input': '[name="firstName"], [data-cy="first-name-input"]',
  'last-name-input': '[name="lastName"], [data-cy="last-name-input"]',
  'terms-checkbox': '[name="terms"], [data-cy="terms-checkbox"]',
  
  // Layout selectors
  'main-content': 'main, .main-content, [role="main"], [data-cy="main-content"]',
  'user-menu': '.user-menu, [data-cy="user-menu"], .dropdown-toggle',
  'loading-screen': '.loading, .spinner, [data-cy="loading-screen"]',
  
  // Language selectors (may not exist)
  'language-selector': '[data-cy="language-selector"], .language-selector, select[name="language"]',
  'language-option-he': '[value="he"], [data-cy="language-option-he"]',
  'language-option-en': '[value="en"], [data-cy="language-option-en"]',
  
  // Error message selectors
  'login-error': '.error, .alert-error, [data-cy="login-error"], .error-message',
  'signup-error': '.error, .alert-error, [data-cy="signup-error"], .error-message',
  'error-message': '.error, .alert-error, .error-message, [role="alert"]',
  
  // Admin selectors
  'admin-dashboard': '.admin-dashboard, [data-cy="admin-dashboard"]',
  'admin-title': 'h1, .admin-title, [data-cy="admin-title"]'
}

// Helper function to get selector
export const getSelector = (key) => {
  return selectors[key] || `[data-cy="${key}"]`
}

// Add to Cypress commands
Cypress.Commands.add('getBySelector', (selectorKey, options) => {
  const selector = getSelector(selectorKey)
  return cy.get(selector, options)
}) 