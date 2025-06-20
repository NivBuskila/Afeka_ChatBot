// Complete User Journey E2E Tests
// Simplified tests focusing on basic chat functionality without complex login flows

describe('Complete User Journey', () => {
  beforeEach(() => {
    cy.clearAllStorage()
    cy.setupCommonInterceptors()
  })

  it('should handle basic chat functionality directly', () => {
    // Go directly to chat (skip login complexity)
    cy.visit('/chat')
    cy.waitForApp()
    
    // Step 1: First Chat Message
    cy.get('[data-testid="chat-input"]').should('be.visible')
    cy.get('[data-testid="chat-input"]').type('Hello, I need help with course registration')
    cy.get('[data-testid="send-button"]').click()
    
    // Verify chat input is cleared after sending
    cy.get('[data-testid="chat-input"]').should('have.value', '')
    
    // Step 2: Send another message
    cy.get('[data-testid="chat-input"]').type('What are the admission requirements?')
    cy.get('[data-testid="send-button"]').click()
    
    // Verify second message was sent
    cy.get('[data-testid="chat-input"]').should('have.value', '')
    
    // Step 3: Test Enter key functionality
    cy.get('[data-testid="chat-input"]').type('Can you help me with scheduling?')
    cy.get('[data-testid="chat-input"]').type('{enter}')
    
    // Verify message sent with Enter key
    cy.get('[data-testid="chat-input"]').should('have.value', '')
  })

  it('should handle mixed language chat flow', () => {
    cy.visit('/chat')
    cy.waitForApp()
    
    // Test English message
    cy.get('[data-testid="chat-input"]').type('Hello, I need help')
    cy.get('[data-testid="send-button"]').click()
    cy.get('[data-testid="chat-input"]').should('have.value', '')
    
    // Test Hebrew message
    cy.get('[data-testid="chat-input"]').type('שלום, אני צריך עזרה')
    cy.get('[data-testid="send-button"]').click()
    cy.get('[data-testid="chat-input"]').should('have.value', '')
    
    // Test mixed language
    cy.get('[data-testid="chat-input"]').type('שלום, what time is the Computer Science office open?')
    cy.get('[data-testid="send-button"]').click()
    cy.get('[data-testid="chat-input"]').should('have.value', '')
  })

  it('should maintain functionality across page refreshes', () => {
    cy.visit('/chat')
    cy.waitForApp()
    
    // Send a message before refresh
    cy.get('[data-testid="chat-input"]').type('Message before refresh')
    cy.get('[data-testid="send-button"]').click()
    cy.get('[data-testid="chat-input"]').should('have.value', '')
    
    // Refresh page
    cy.reload()
    cy.waitForApp()
    
    // Verify chat functionality still works
    cy.get('[data-testid="chat-input"]').should('be.visible')
    cy.get('[data-testid="chat-input"]').type('Message after refresh')
    cy.get('[data-testid="send-button"]').click()
    cy.get('[data-testid="chat-input"]').should('have.value', '')
  })

  it('should handle rapid message sending', () => {
    cy.visit('/chat')
    cy.waitForApp()
    
    // Test rapid message sending
    const messages = [
      'First quick message',
      'Second quick message', 
      'Third quick message'
    ]
    
    messages.forEach((message, index) => {
      cy.get('[data-testid="chat-input"]').type(message)
      cy.get('[data-testid="send-button"]').click()
      cy.get('[data-testid="chat-input"]').should('have.value', '')
      
      if (index < messages.length - 1) {
        cy.wait(200) // Brief pause between messages
      }
    })
  })
}) 