// Test for navigation flow
describe('Navigation Tests', () => {
  beforeEach(() => {
    // Visit the home page before each test
    cy.visit('/')
  })

  it('should load the home page successfully', () => {
    // Check that the page has loaded
    cy.get('#root').should('exist')
    
    // Check that the title is correct
    cy.title().should('include', 'Afeka ChatBot')
  })

  it('should display the splash screen or login form', () => {
    // Check for either splash screen or login form elements
    cy.get('body').should('contain.text', 'APEX')
  })

  it('should navigate to chat page via URL', () => {
    // Navigate directly to chat page
    cy.visit('/chat')
    
    // Check if chat interface is displayed
    cy.url().should('include', '/chat')
    cy.get('[data-testid="chat-container"]', { timeout: 10000 }).should('exist')
  })

  it('should navigate to dashboard page via URL', () => {
    // Navigate directly to dashboard page
    cy.visit('/dashboard')
    
    // Check if dashboard is displayed (might redirect to login if not authenticated)
    cy.url().should('match', /\/(dashboard|$)/)
  })

  it('should navigate to registration page via URL', () => {
    // Navigate directly to registration page
    cy.visit('/register')
    
    // Check if registration page is displayed
    cy.url().should('include', '/register')
  })

  it('should navigate to terms page via URL', () => {
    // Navigate directly to terms page
    cy.visit('/terms-and-conditions')
    
    // Check if terms page is displayed
    cy.url().should('include', '/terms-and-conditions')
  })
}) 