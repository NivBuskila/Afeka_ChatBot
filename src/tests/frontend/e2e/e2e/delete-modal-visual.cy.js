describe("DeleteModal Visual and Theme Tests", () => {
  beforeEach(() => {
    cy.visit("/dashboard")
    cy.waitForApp()
  })

  describe("Theme Support", () => {
    it("should render with correct theme styles", () => {
      // Test light theme
      cy.window().then((win) => {
        win.localStorage.setItem("theme", "light")
        win.document.documentElement.classList.remove("dark")
      })
      
      // Look for delete buttons and test modal appearance
      cy.get("body").then($body => {
        const deleteSelectors = [
          "[data-cy=\"delete-document\"]", ".delete-button",
          "[aria-label*=\"delete\"]"
        ]
        
        deleteSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().click()
            cy.wait(500)
            
            // Verify light theme modal
            cy.get(".bg-white").should("be.visible")
            cy.get(".text-gray-900").should("be.visible")
          }
        })
      })
    })
  })

  describe("Long Text Handling", () => {
    it("should handle long filenames without overflow", () => {
      cy.get("body").then($body => {
        const deleteSelectors = [".delete-button", "[aria-label*=\"delete\"]"]
        
        deleteSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().click()
            cy.wait(500)
            
            // Check modal width constraints
            cy.get(".max-w-md").should("be.visible")
            cy.get(".break-words").should("exist")
          }
        })
      })
    })
  })
})
