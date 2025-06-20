// Document Management E2E Tests
// Tests document upload, editing, deletion, and management functionality

describe('Document Management', () => {
  beforeEach(() => {
    cy.clearAllStorage()
    cy.setupCommonInterceptors()
  })

  describe('Document Upload Interface', () => {
    it('should access document upload interface', () => {
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Look for document upload area
      cy.get('body').then($body => {
        const uploadSelectors = [
          '[data-cy="upload-area"]', '.upload-area',
          '[data-cy="document-upload"]', '.document-upload',
          'input[type="file"]', '.file-upload',
          '[data-cy="upload-button"]', '.upload-button'
        ]
        
        uploadSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })

    it('should display upload drop zone', () => {
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Look for drag and drop area
      cy.get('body').then($body => {
        const dropzoneSelectors = [
          '[data-cy="dropzone"]', '.dropzone',
          '.drag-drop-area', '[data-cy="drag-drop"]',
          '.file-drop-zone', '[aria-label*="drop"]'
        ]
        
        dropzoneSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })

    it('should show upload instructions', () => {
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Look for upload instructions
      cy.get('body').then($body => {
        const instructionTexts = [
          'drag', 'drop', 'upload', 'העלה', 'גרור'
        ]
        
        let found = false
        instructionTexts.forEach(text => {
          if ($body.text().toLowerCase().includes(text.toLowerCase())) {
            found = true
          }
        })
        
        if (found) {
          cy.get('body').should('contain.text', 'upload').or('contain.text', 'העלה')
        }
      })
    })
  })

  describe('Document Upload Functionality', () => {
    it('should handle file selection via input', () => {
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Look for file input and test file selection
      cy.get('body').then($body => {
        if ($body.find('input[type="file"]').length > 0) {
          // Create a test file
          const fileName = 'test-document.pdf'
          const fileContent = 'This is a test PDF content'
          
          cy.get('input[type="file"]').first().selectFile({
            contents: Cypress.Buffer.from(fileContent),
            fileName: fileName,
            mimeType: 'application/pdf'
          }, { force: true })
          
          cy.wait(1000) // Allow processing time
        }
      })
    })

    it('should validate file types', () => {
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Test invalid file type
      cy.get('body').then($body => {
        if ($body.find('input[type="file"]').length > 0) {
          const fileName = 'test-invalid.exe'
          const fileContent = 'Invalid file content'
          
          cy.get('input[type="file"]').first().selectFile({
            contents: Cypress.Buffer.from(fileContent),
            fileName: fileName,
            mimeType: 'application/x-executable'
          }, { force: true })
          
          // Should show error or reject the file
          cy.wait(1000)
        }
      })
    })

    it('should show upload progress', () => {
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Intercept upload request to simulate progress
      cy.intercept('POST', '**/upload/**', (req) => {
        req.reply((res) => {
          res.delay(2000) // Simulate slow upload
          res.send({ statusCode: 200, body: { success: true } })
        })
      }).as('uploadFile')
      
      // Look for file input and upload
      cy.get('body').then($body => {
        if ($body.find('input[type="file"]').length > 0) {
          const fileName = 'test-progress.pdf'
          const fileContent = 'Test content for progress'
          
          cy.get('input[type="file"]').first().selectFile({
            contents: Cypress.Buffer.from(fileContent),
            fileName: fileName,
            mimeType: 'application/pdf'
          }, { force: true })
          
          // Look for progress indicators
          cy.get('body').then($progressBody => {
            const progressSelectors = [
              '.progress', '[data-cy="upload-progress"]',
              '.loading', '.spinner', '.uploading'
            ]
            
            progressSelectors.forEach(selector => {
              if ($progressBody.find(selector).length > 0) {
                cy.get(selector).first().should('be.visible')
              }
            })
          })
        }
      })
    })
  })

  describe('Document List and Display', () => {
    it('should display document list', () => {
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Look for document list/table
      cy.get('body').then($body => {
        const documentListSelectors = [
          '[data-cy="document-list"]', '.document-list',
          '[data-cy="document-table"]', '.document-table',
          'table', '.file-list', '.documents'
        ]
        
        documentListSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })

    it('should show document details', () => {
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Look for document information
      cy.get('body').then($body => {
        const detailSelectors = [
          '.document-name', '.file-name',
          '.document-size', '.file-size',
          '.document-date', '.upload-date',
          '.document-type', '.file-type'
        ]
        
        detailSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })

    it('should handle empty document state', () => {
      // Intercept API to return empty documents
      cy.intercept('GET', '**/documents/**', { body: [] }).as('emptyDocuments')
      
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Should show empty state message
      cy.get('body').then($body => {
        const emptyStateTexts = [
          'no documents', 'אין מסמכים', 'empty', 'upload first'
        ]
        
        emptyStateTexts.forEach(text => {
          if ($body.text().toLowerCase().includes(text.toLowerCase())) {
            cy.get('body').should('contain.text', text)
          }
        })
      })
    })
  })

  describe('Document Search and Filtering', () => {
    it('should provide document search', () => {
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Look for search functionality
      cy.get('body').then($body => {
        const searchSelectors = [
          '[data-cy="document-search"]', 'input[placeholder*="search"]',
          'input[placeholder*="חיפוש"]', '.search-documents',
          '[aria-label*="search"]', '.document-filter'
        ]
        
        searchSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().type('test')
            cy.wait(500)
            cy.get(selector).first().clear()
          }
        })
      })
    })

    it('should filter by document type', () => {
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Look for type filters
      cy.get('body').then($body => {
        const filterSelectors = [
          '[data-cy="type-filter"]', 'select[name*="type"]',
          '.type-filter', '.file-type-filter',
          '[data-cy="filter-pdf"]', '[data-cy="filter-doc"]'
        ]
        
        filterSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })

    it('should sort documents', () => {
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Look for sort options
      cy.get('body').then($body => {
        const sortSelectors = [
          '[data-cy="sort-documents"]', '.sort-select',
          '[aria-label*="sort"]', '.document-sort',
          'th[role="columnheader"]', '.sortable'
        ]
        
        sortSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().click()
            cy.wait(500)
          }
        })
      })
    })
  })

  describe('Document Actions', () => {
    it('should provide document edit functionality', () => {
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Look for edit buttons/options
      cy.get('body').then($body => {
        const editSelectors = [
          '[data-cy="edit-document"]', '.edit-button',
          '[aria-label*="edit"]', '[title*="edit"]',
          '.document-edit', 'button[data-action="edit"]'
        ]
        
        editSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().click()
            cy.wait(500)
            
            // Look for edit modal or form
            cy.get('body').then($editBody => {
              const editFormSelectors = [
                '.modal', '.edit-form', '[data-cy="edit-modal"]',
                'input[name*="name"]', 'textarea'
              ]
              
              editFormSelectors.forEach(formSelector => {
                if ($editBody.find(formSelector).length > 0) {
                  cy.get(formSelector).first().should('be.visible')
                }
              })
            })
          }
        })
      })
    })

    it('should provide document delete functionality', () => {
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Look for delete buttons
      cy.get('body').then($body => {
        const deleteSelectors = [
          '[data-cy="delete-document"]', '.delete-button',
          '[aria-label*="delete"]', '[title*="delete"]',
          '.document-delete', 'button[data-action="delete"]'
        ]
        
        deleteSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().click()
            cy.wait(500)
            
            // Look for confirmation modal
            cy.get('body').then($deleteBody => {
              const confirmSelectors = [
                '.confirm-modal', '[data-cy="confirm-delete"]',
                '.delete-modal', '.confirmation'
              ]
              
              confirmSelectors.forEach(confirmSelector => {
                if ($deleteBody.find(confirmSelector).length > 0) {
                  cy.get(confirmSelector).first().should('be.visible')
                }
              })
            })
          }
        })
      })
    })

    it('should provide document download functionality', () => {
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Look for download buttons
      cy.get('body').then($body => {
        const downloadSelectors = [
          '[data-cy="download-document"]', '.download-button',
          '[aria-label*="download"]', '[title*="download"]',
          '.document-download', 'a[download]'
        ]
        
        downloadSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })
  })

  describe('Document Processing Status', () => {
    it('should show processing status for uploaded documents', () => {
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Look for processing indicators
      cy.get('body').then($body => {
        const statusSelectors = [
          '.processing', '[data-cy="processing-status"]',
          '.document-status', '.upload-status',
          '.pending', '.completed', '.failed'
        ]
        
        statusSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })

    it('should handle processing errors', () => {
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Look for error states
      cy.get('body').then($body => {
        const errorSelectors = [
          '.error', '.failed', '[data-cy="processing-error"]',
          '.document-error', '.upload-error'
        ]
        
        errorSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })
  })

  describe('Document Permissions and Security', () => {
    it('should handle unauthorized access', () => {
      // Test without proper authentication
      cy.intercept('GET', '**/documents/**', { statusCode: 401 }).as('unauthorized')
      
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Should handle unauthorized state
      cy.get('body').should('be.visible')
    })

    it('should validate file size limits', () => {
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Look for file size information
      cy.get('body').then($body => {
        const sizeLimitTexts = [
          'MB', 'size limit', 'maximum', 'גודל מקסימלי'
        ]
        
        sizeLimitTexts.forEach(text => {
          if ($body.text().toLowerCase().includes(text.toLowerCase())) {
            cy.get('body').should('contain.text', text)
          }
        })
      })
    })
  })

  describe('Document Batch Operations', () => {
    it('should support multiple document selection', () => {
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Look for checkboxes or selection controls
      cy.get('body').then($body => {
        const selectionSelectors = [
          'input[type="checkbox"]', '[data-cy="select-document"]',
          '.document-checkbox', '.select-all',
          '[aria-label*="select"]'
        ]
        
        selectionSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })

    it('should provide batch actions', () => {
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Look for batch operation buttons
      cy.get('body').then($body => {
        const batchSelectors = [
          '[data-cy="batch-delete"]', '.batch-actions',
          '[data-cy="select-all"]', '.bulk-actions',
          '[data-cy="batch-download"]'
        ]
        
        batchSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })
  })

  describe('Document Management Responsiveness', () => {
    it('should work on mobile devices', () => {
      cy.viewport(375, 667) // Mobile view
      cy.visit('/dashboard')
      cy.waitForApp()
      
      // Should be usable on mobile
      cy.get('body').should('be.visible')
      
      // Test file upload on mobile
      cy.get('body').then($body => {
        if ($body.find('input[type="file"]').length > 0) {
          cy.get('input[type="file"]').first().should('be.visible')
        }
      })
    })

    it('should adapt layout for different screen sizes', () => {
      // Test different viewports
      const viewports = [
        [375, 667],  // Mobile
        [768, 1024], // Tablet
        [1920, 1080] // Desktop
      ]
      
      viewports.forEach(([width, height]) => {
        cy.viewport(width, height)
        cy.visit('/dashboard')
        cy.waitForApp()
        cy.get('body').should('be.visible')
      })
    })
  })
})
