describe('Chat Interaction', () => {
  beforeEach(() => {
    // Visit the homepage before each test
    cy.visit('/');
    
    // Wait for app to load fully
    cy.get('body').should('be.visible');
    cy.wait(1000); // Allow any initial animations to complete
  });

  it('should display chat interface', () => {
    // Verify that chat input is present
    cy.get('[data-testid="chat-input"]').should('exist');
    cy.get('[data-testid="send-button"]').should('exist');
  });

  it('should send a message and receive a response', () => {
    // Type a message
    cy.get('[data-testid="chat-input"]').type('What are the regulations for exams?');
    
    // Send the message
    cy.get('[data-testid="send-button"]').click();
    
    // Wait for response (with timeout)
    cy.get('[data-testid="message-container"]', { timeout: 10000 })
      .should('contain', 'What are the regulations for exams?');
    
    // Check for a response from the assistant
    cy.get('[data-testid="message-container"]')
      .should('contain', 'regulations');
  });

  it('should display error for empty message', () => {
    // Try to send an empty message
    cy.get('[data-testid="send-button"]').click();
    
    // Button should be disabled for empty messages
    cy.get('[data-testid="send-button"]').should('be.disabled');
  });

  it('should handle long conversations', () => {
    // Send first message
    cy.get('[data-testid="chat-input"]').type('Hello');
    cy.get('[data-testid="send-button"]').click();
    
    // Wait for the first response
    cy.wait(2000);
    
    // Send follow-up message
    cy.get('[data-testid="chat-input"]').type('Tell me about academic regulations');
    cy.get('[data-testid="send-button"]').click();
    
    // Check that both messages appear in the conversation
    cy.get('[data-testid="message-container"]').should('contain', 'Hello');
    cy.get('[data-testid="message-container"]').should('contain', 'academic regulations');
  });
}); 