describe('Navigation', () => {
  beforeEach(() => {
    // Visit the homepage before each test
    cy.visit('/');
    cy.wait(1000); // Wait for app to load
  });

  it('should navigate to main pages', () => {
    // Check that we're on the home page
    cy.url().should('include', '/');
    
    // Navigate to settings page if it exists
    cy.get('nav').then($nav => {
      if ($nav.find('[data-testid="settings-link"]').length) {
        cy.get('[data-testid="settings-link"]').click();
        cy.url().should('include', '/settings');
        
        // Go back to home
        cy.get('[data-testid="home-link"]').click();
        cy.url().should('include', '/');
      }
    });
  });

  it('should show/hide sidebar when toggled', () => {
    // Look for a sidebar toggle button
    cy.get('body').then($body => {
      if ($body.find('[data-testid="sidebar-toggle"]').length) {
        // Open sidebar if it's not already open
        cy.get('[data-testid="sidebar-toggle"]').click();
        cy.get('[data-testid="sidebar"]').should('be.visible');
        
        // Close sidebar
        cy.get('[data-testid="sidebar-toggle"]').click();
        cy.get('[data-testid="sidebar"]').should('not.be.visible');
      }
    });
  });

  it('should handle dark mode toggle', () => {
    // Look for dark mode toggle
    cy.get('body').then($body => {
      if ($body.find('[data-testid="theme-toggle"]').length) {
        // Check initial theme state
        const initialTheme = $body.hasClass('dark') ? 'dark' : 'light';
        
        // Toggle theme
        cy.get('[data-testid="theme-toggle"]').click();
        
        // Verify theme changed
        if (initialTheme === 'dark') {
          cy.get('body').should('not.have.class', 'dark');
        } else {
          cy.get('body').should('have.class', 'dark');
        }
      }
    });
  });
}); 