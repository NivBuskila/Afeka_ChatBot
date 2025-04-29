// Test for chat widget interactions
describe('Chat Widget Tests', () => {
  beforeEach(() => {
    // Visit the chat page before each test
    cy.visit('/chat')
    
    // Wait for chat component to load
    cy.get('[data-testid="chat-container"]', { timeout: 10000 }).should('exist')
  })

  it('should display the chat interface', () => {
    // Check that chat input exists
    cy.get('[data-testid="chat-input"]').should('exist')
    
    // Check that send button exists
    cy.get('[data-testid="send-button"]').should('exist')
    
    // Check that chat history container exists
    cy.get('[data-testid="chat-history"]').should('exist')
  })

  it('should allow typing in the chat input', () => {
    const testMessage = 'Hello, this is a test message'
    
    // Type a message in the chat input
    cy.get('[data-testid="chat-input"]').type(testMessage)
    
    // Verify the message was typed
    cy.get('[data-testid="chat-input"]').should('have.value', testMessage)
  })

  it('should send a message and receive a response', () => {
    const testMessage = 'What is Afeka College?'
    
    // Type a message
    cy.get('[data-testid="chat-input"]').type(testMessage)
    
    // Click send button
    cy.get('[data-testid="send-button"]').click()
    
    // Verify user message appears in chat history
    cy.get('[data-testid="user-message"]').should('contain', testMessage)
    
    // Wait for bot response (with longer timeout)
    cy.get('[data-testid="bot-message"]', { timeout: 30000 }).should('exist')
  })

  it('should clear chat input after sending', () => {
    const testMessage = 'Test clearing input'
    
    // Type a message
    cy.get('[data-testid="chat-input"]').type(testMessage)
    
    // Click send button
    cy.get('[data-testid="send-button"]').click()
    
    // Check input was cleared
    cy.get('[data-testid="chat-input"]').should('have.value', '')
  })

  it('should show typing indicator when waiting for response', () => {
    const testMessage = 'Show me typing indicator'
    
    // Type a message
    cy.get('[data-testid="chat-input"]').type(testMessage)
    
    // Click send button
    cy.get('[data-testid="send-button"]').click()
    
    // Check for typing indicator (should appear immediately)
    cy.get('[data-testid="typing-indicator"]', { timeout: 2000 }).should('exist')
  })

  it('should allow sending message with Enter key', () => {
    const testMessage = 'Sending with Enter key'
    
    // Type a message and press Enter
    cy.get('[data-testid="chat-input"]').type(testMessage).type('{enter}')
    
    // Verify message appears in chat
    cy.get('[data-testid="user-message"]').should('contain', testMessage)
  })
}) 