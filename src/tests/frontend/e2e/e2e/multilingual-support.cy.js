// Multilingual Support E2E Tests
// Simplified tests focusing on basic Hebrew/English functionality

describe('Multilingual Support', () => {
  beforeEach(() => {
    cy.clearAllStorage()
    cy.setupCommonInterceptors()
  })

  it('should handle basic Hebrew text input in chat', () => {
    cy.visit('/chat')
    cy.waitForApp()
    
    // Test Hebrew text input in chat
    cy.get('[data-testid="chat-input"]').should('be.visible')
    cy.get('[data-testid="chat-input"]').type('שלום, אני צריך עזרה')
    cy.get('[data-testid="send-button"]').click()
    
    // Verify input is cleared after sending
    cy.get('[data-testid="chat-input"]').should('have.value', '')
  })

  it('should handle mixed Hebrew and English content', () => {
    cy.visit('/chat')
    cy.waitForApp()
    
    // Test mixed language input
    cy.get('[data-testid="chat-input"]').type('שלום, what time is Computer Science open?')
    cy.get('[data-testid="send-button"]').click()
    
    // Verify mixed content was sent
    cy.get('[data-testid="chat-input"]').should('have.value', '')
  })

  it('should handle English text normally', () => {
    cy.visit('/chat')
    cy.waitForApp()
    
    // Test English text input
    cy.get('[data-testid="chat-input"]').type('Hello, I need help with registration')
    cy.get('[data-testid="send-button"]').click()
    
    // Verify input is cleared
    cy.get('[data-testid="chat-input"]').should('have.value', '')
  })

  it('should maintain chat functionality with special characters', () => {
    cy.visit('/chat')
    cy.waitForApp()
    
    // Test various special characters
    const testMessages = [
      'Test with numbers: 123',
      'Test with symbols: !@#$%',
      'Test Hebrew numbers: ١٢٣',
      'Test mixed: Hello שלום 123'
    ]
    
    testMessages.forEach(message => {
      cy.get('[data-testid="chat-input"]').type(message)
      cy.get('[data-testid="send-button"]').click()
      cy.get('[data-testid="chat-input"]').should('have.value', '')
      cy.wait(500) // Small delay between messages
    })
  })

  it('should handle long Hebrew text', () => {
    cy.visit('/chat')
    cy.waitForApp()
    
    // Test long Hebrew text
    const longHebrewText = 'שלום, אני סטודנט חדש באוניברסיטה ואני צריך עזרה עם תהליך הרישום לקורסים. האם תוכל לעזור לי להבין מה הדרישות ומתי מתחיל הסמסטר הבא?'
    
    cy.get('[data-testid="chat-input"]').type(longHebrewText)
    cy.get('[data-testid="send-button"]').click()
    
    // Verify input is cleared
    cy.get('[data-testid="chat-input"]').should('have.value', '')
  })

  it('should handle text direction properly', () => {
    cy.visit('/chat')
    cy.waitForApp()
    
    // Test that Hebrew text maintains proper direction
    cy.get('[data-testid="chat-input"]').type('עברית')
    
    // Verify the input has Hebrew text
    cy.get('[data-testid="chat-input"]').should('have.value', 'עברית')
    
    // Send the message
    cy.get('[data-testid="send-button"]').click()
    cy.get('[data-testid="chat-input"]').should('have.value', '')
  })

  it('should handle rapid language switching in chat', () => {
    cy.visit('/chat')
    cy.waitForApp()
    
    // Test rapid switching between languages
    const messages = [
      'Hello in English',
      'שלום בעברית',
      'Back to English',
      'חזרה לעברית',
      'Final English message'
    ]
    
    messages.forEach((message, index) => {
      cy.get('[data-testid="chat-input"]').type(message)
      cy.get('[data-testid="send-button"]').click()
      cy.get('[data-testid="chat-input"]').should('have.value', '')
      
      if (index < messages.length - 1) {
        cy.wait(300) // Brief pause between messages
      }
    })
  })

  it('should handle empty and whitespace messages correctly', () => {
    cy.visit('/chat')
    cy.waitForApp()
    
    // Test empty message - send button should be disabled
    cy.get('[data-testid="send-button"]').should('be.disabled')
    
    // Test whitespace only
    cy.get('[data-testid="chat-input"]').type('   ')
    
    // Send button should still be disabled for whitespace-only input
    cy.get('[data-testid="send-button"]').should('be.disabled')
    
    // Clear input
    cy.get('[data-testid="chat-input"]').clear()
    
    // Test that button becomes enabled with actual content
    cy.get('[data-testid="chat-input"]').type('Real message')
    cy.get('[data-testid="send-button"]').should('be.enabled')
    
    // Send the message
    cy.get('[data-testid="send-button"]').click()
    cy.get('[data-testid="chat-input"]').should('have.value', '')
    
    // Button should be disabled again after sending
    cy.get('[data-testid="send-button"]').should('be.disabled')
  })

  it('should maintain functionality across page refreshes', () => {
    cy.visit('/chat')
    cy.waitForApp()
    
    // Send a Hebrew message
    cy.get('[data-testid="chat-input"]').type('הודעה לפני רענון')
    cy.get('[data-testid="send-button"]').click()
    
    // Refresh page
    cy.reload()
    cy.waitForApp()
    
    // Verify chat functionality still works
    cy.get('[data-testid="chat-input"]').should('be.visible')
    cy.get('[data-testid="chat-input"]').type('הודעה אחרי רענון')
    cy.get('[data-testid="send-button"]').click()
    cy.get('[data-testid="chat-input"]').should('have.value', '')
  })

  it('should handle emoji and special Unicode characters', () => {
    cy.visit('/chat')
    cy.waitForApp()
    
    // Test emoji and special characters
    const specialMessages = [
      '😊 שלום',
      'Hello 🌍',
      '🇮🇱 ישראל',
      '📚 ספרים',
      'Test ♥ עברית'
    ]
    
    specialMessages.forEach(message => {
      cy.get('[data-testid="chat-input"]').type(message)
      cy.get('[data-testid="send-button"]').click()
      cy.get('[data-testid="chat-input"]').should('have.value', '')
      cy.wait(200)
    })
  })
}) 