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

  it('should display the main navigation elements', () => {
    // Check for main navigation elements
    cy.get('nav').should('exist')
  })

  it('should navigate to chat page', () => {
    // Find and click the chat link
    cy.contains('Chat').click()
    
    // Check if chat interface is displayed
    cy.url().should('include', '/chat')
    cy.get('[data-testid="chat-container"]').should('exist')
  })

  it('should navigate to documents page', () => {
    // Find and click the documents link
    cy.contains('Documents').click()
    
    // Check if documents page is displayed
    cy.url().should('include', '/documents')
    cy.get('[data-testid="documents-container"]').should('exist')
  })

  it('should navigate to about page', () => {
    // Find and click the about link
    cy.contains('About').click()
    
    // Check if about page is displayed
    cy.url().should('include', '/about')
    cy.get('[data-testid="about-container"]').should('exist')
  })

  it('should navigate back to home from other pages', () => {
    // Go to chat page
    cy.contains('Chat').click()
    
    // Then go back to home
    cy.contains('Home').click()
    
    // Verify we're on the home page
    cy.url().should('not.include', '/chat')
    cy.get('[data-testid="home-container"]').should('exist')
  })
}) 