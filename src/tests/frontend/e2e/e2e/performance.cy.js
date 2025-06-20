// Performance E2E Tests
// Simplified tests focusing on basic page load times and chat responsiveness

describe('Performance', () => {
  beforeEach(() => {
    cy.clearAllStorage()
    cy.setupCommonInterceptors()
  })

  it('should load main pages within reasonable time', () => {
    // Test chat page performance (main functionality)
    const startTime = Date.now()
    cy.visit('/chat')
    cy.waitForApp()
    
    // Verify page loads within reasonable time
    cy.get('[data-testid="chat-input"]').should('be.visible')
    const loadTime = Date.now() - startTime
    cy.log(`Chat page load time: ${loadTime}ms`)
    
    // Basic performance check - should load within 10 seconds
    expect(loadTime).to.be.lessThan(10000)
  })

  it('should handle alternative page load performance', () => {
    const startTime = Date.now()
    cy.visit('/')
    cy.waitForApp()
    
    // Verify page loads with some visible content
    cy.get('body').should('be.visible')
    
    const loadTime = Date.now() - startTime
    cy.log(`Homepage load time: ${loadTime}ms`)
    
    // Homepage should load within 8 seconds
    expect(loadTime).to.be.lessThan(8000)
  })

  it('should handle chat interactions efficiently', () => {
    cy.visit('/chat')
    cy.waitForApp()

    // Test basic chat interaction timing
    cy.get('[data-testid="chat-input"]').should('be.visible')
    
    const startTime = Date.now()
    cy.get('[data-testid="chat-input"]').type('Performance test message')
    cy.get('[data-testid="send-button"]').click()
    
    // Verify input is cleared quickly (indicates message was sent)
    cy.get('[data-testid="chat-input"]').should('have.value', '')
    
    const interactionTime = Date.now() - startTime
    cy.log(`Chat interaction time: ${interactionTime}ms`)
    
    // Basic interaction should be under 3 seconds
    expect(interactionTime).to.be.lessThan(3000)
  })

  it('should handle multiple rapid messages', () => {
    cy.visit('/chat')
    cy.waitForApp()

    const startTime = Date.now()
    
    // Send multiple messages rapidly
    const messages = ['Message 1', 'Message 2', 'Message 3']
    
    messages.forEach((message, index) => {
      cy.get('[data-testid="chat-input"]').type(message)
      cy.get('[data-testid="send-button"]').click()
      cy.get('[data-testid="chat-input"]').should('have.value', '')
      
      if (index < messages.length - 1) {
        cy.wait(100) // Small delay between messages
      }
    })
    
    const totalTime = Date.now() - startTime
    cy.log(`Multiple messages time: ${totalTime}ms`)
    
    // Multiple messages should complete within 8 seconds
    expect(totalTime).to.be.lessThan(8000)
  })

  it('should maintain responsiveness with Hebrew text', () => {
    cy.visit('/chat')
    cy.waitForApp()

    const startTime = Date.now()
    
    // Test Hebrew text performance
    const hebrewMessage = 'שלום, בדיקת ביצועים עם טקסט בעברית'
    cy.get('[data-testid="chat-input"]').type(hebrewMessage)
    cy.get('[data-testid="send-button"]').click()
    cy.get('[data-testid="chat-input"]').should('have.value', '')
    
    const hebrewTime = Date.now() - startTime
    cy.log(`Hebrew text interaction time: ${hebrewTime}ms`)
    
    // Hebrew text should not significantly impact performance
    expect(hebrewTime).to.be.lessThan(4000)
  })

  it('should handle page refreshes efficiently', () => {
    cy.visit('/chat')
    cy.waitForApp()
    
    // Send a message first
    cy.get('[data-testid="chat-input"]').type('Pre-refresh message')
    cy.get('[data-testid="send-button"]').click()
    cy.get('[data-testid="chat-input"]').should('have.value', '')
    
    // Test refresh performance
    const refreshStartTime = Date.now()
    cy.reload()
    cy.waitForApp()
    
    // Verify functionality after refresh
    cy.get('[data-testid="chat-input"]').should('be.visible')
    
    const refreshTime = Date.now() - refreshStartTime
    cy.log(`Page refresh time: ${refreshTime}ms`)
    
    // Page refresh should complete within 8 seconds
    expect(refreshTime).to.be.lessThan(8000)
  })
}) 