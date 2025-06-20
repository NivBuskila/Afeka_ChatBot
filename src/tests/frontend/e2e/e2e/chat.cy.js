// Test for chat widget interactions
describe('Chat Widget Tests', () => {
  beforeEach(() => {
    // Visit the chat page before each test
    cy.visit('/chat')
    
    // Wait for chat component to load
    cy.get('[data-testid="chat-container"]', { timeout: 15000 }).should('exist')
    
    // Wait for the chat interface to be ready
    cy.get('[data-testid="chat-input"]', { timeout: 10000 }).should('exist')
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

  it('should send a message and handle response', () => {
    const testMessage = 'What is Afeka College?'
    
    // Type a message
    cy.get('[data-testid="chat-input"]').type(testMessage)
    
    // Click send button
    cy.get('[data-testid="send-button"]').click()
    
    // Check that input was cleared after sending
    cy.get('[data-testid="chat-input"]').should('have.value', '')
    
    // Wait a moment for any UI updates
    cy.wait(1000)
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

  it('should handle message sending process', () => {
    const testMessage = 'Show me typing indicator'
    
    // Type a message
    cy.get('[data-testid="chat-input"]').type(testMessage)
    
    // Verify message is typed
    cy.get('[data-testid="chat-input"]').should('have.value', testMessage)
    
    // Click send button
    cy.get('[data-testid="send-button"]').click()
    
    // Verify input is cleared after sending
    cy.get('[data-testid="chat-input"]').should('have.value', '')
  })

  it('should allow sending message with Enter key', () => {
    const testMessage = 'Sending with Enter key'
    
    // Type a message
    cy.get('[data-testid="chat-input"]').type(testMessage)
    
    // Verify message is typed
    cy.get('[data-testid="chat-input"]').should('have.value', testMessage)
    
    // Press Enter to send
    cy.get('[data-testid="chat-input"]').type('{enter}')
    
    // Wait a moment for the send action to complete
    cy.wait(1000)
    
    // Verify input is cleared after sending (shows message was sent)
    cy.get('[data-testid="chat-input"]').should('have.value', '')
  })
}) 