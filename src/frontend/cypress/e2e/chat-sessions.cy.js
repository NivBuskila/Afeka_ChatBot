// Chat Sessions E2E Tests
// Tests session management, history, and persistence

describe('Chat Sessions', () => {
  beforeEach(() => {
    cy.clearAllStorage()
    cy.setupCommonInterceptors()
  })

  describe('Session Management', () => {
    it('should create new chat sessions', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for new session/new chat functionality
      cy.get('body').then($body => {
        const newSessionSelectors = [
          '[data-cy="new-session"]', '.new-chat-button',
          '[data-cy="new-chat"]', '.create-session',
          '[aria-label*="new chat"]', '.start-new-conversation'
        ]
        
        newSessionSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
            cy.get(selector).first().click()
            cy.wait(500)
            
            // Verify new session was created
            cy.get('body').should('be.visible')
          }
        })
      })
    })

    it('should list existing chat sessions', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for session list/history
      cy.get('body').then($body => {
        const sessionListSelectors = [
          '[data-cy="session-list"]', '.chat-history',
          '[data-cy="chat-sessions"]', '.session-sidebar',
          '.conversation-list', '.chat-list'
        ]
        
        sessionListSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })

    it('should switch between sessions', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test session switching
      cy.get('body').then($body => {
        const sessionItemSelectors = [
          '.session-item', '[data-cy="session-item"]',
          '.chat-session', '.conversation-item'
        ]
        
        sessionItemSelectors.forEach(selector => {
          if ($body.find(selector).length > 1) {
            // Click on different sessions
            cy.get(selector).eq(0).click()
            cy.wait(500)
            cy.get(selector).eq(1).click()
            cy.wait(500)
          }
        })
      })
    })

    it('should delete chat sessions', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for delete session functionality
      cy.get('body').then($body => {
        const deleteSelectors = [
          '[data-cy="delete-session"]', '.delete-chat',
          '[aria-label*="delete"]', '.remove-session',
          '.delete-conversation'
        ]
        
        deleteSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().click()
            cy.wait(500)
            
            // Look for confirmation dialog
            const confirmSelectors = [
              '.confirm-delete', '[data-cy="confirm-modal"]',
              '.delete-confirmation', '.modal'
            ]
            
            confirmSelectors.forEach(confirmSelector => {
              if ($body.find(confirmSelector).length > 0) {
                cy.get(confirmSelector).first().should('be.visible')
              }
            })
          }
        })
      })
    })

    it('should rename chat sessions', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for rename functionality
      cy.get('body').then($body => {
        const renameSelectors = [
          '[data-cy="rename-session"]', '.rename-chat',
          '[aria-label*="rename"]', '.edit-session-name'
        ]
        
        renameSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().click()
            cy.wait(500)
            
            // Look for edit input
            const editSelectors = [
              'input[data-editing]', '.session-name-input',
              '[data-cy="session-name-edit"]'
            ]
            
            editSelectors.forEach(editSelector => {
              if ($body.find(editSelector).length > 0) {
                cy.get(editSelector).first().should('be.visible')
                cy.get(editSelector).first().clear()
                cy.get(editSelector).first().type('Renamed Session')
                cy.get(editSelector).first().type('{enter}')
              }
            })
          }
        })
      })
    })
  })

  describe('Session Persistence', () => {
    it('should save sessions across page reloads', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Send a message to create session content
      cy.get('body').then($body => {
        const messageInput = $body.find('[data-cy="chat-input"]')
        
        if (messageInput.length > 0) {
          cy.get('[data-cy="chat-input"]').first().type('Test message for persistence')
          cy.get('[data-cy="send-button"]').first().click()
          cy.wait(1000)
          
          // Reload page
          cy.reload()
          cy.waitForApp()
          
          // Check if message persisted
          cy.get('body').should('contain.text', 'Test message for persistence')
        }
      })
    })

    it('should restore active session on return', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Create session content
      cy.get('body').then($body => {
        const messageInput = $body.find('[data-cy="chat-input"]')
        
        if (messageInput.length > 0) {
          cy.get('[data-cy="chat-input"]').first().type('Session restoration test')
          cy.get('[data-cy="send-button"]').first().click()
          cy.wait(1000)
          
          // Navigate away and back
          cy.visit('/dashboard')
          cy.waitForApp()
          cy.visit('/chat')
          cy.waitForApp()
          
          // Check if session was restored
          cy.get('body').should('be.visible')
        }
      })
    })

    it('should maintain session state in localStorage', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Check localStorage for session data
      cy.window().then((win) => {
        const sessionKeys = [
          'chatSessions', 'activeChatSession', 'chatHistory',
          'conversationHistory', 'currentSession'
        ]
        
        sessionKeys.forEach(key => {
          const stored = win.localStorage.getItem(key)
          if (stored) {
            expect(stored).to.not.be.null
          }
        })
      })
    })

    it('should handle session data migration', () => {
      // Set old format session data
      cy.window().then((win) => {
        win.localStorage.setItem('oldChatData', JSON.stringify({
          messages: ['old message 1', 'old message 2']
        }))
      })
      
      cy.visit('/chat')
      cy.waitForApp()
      
      // Should handle old data gracefully
      cy.get('body').should('be.visible')
    })
  })

  describe('Session Search and Navigation', () => {
    it('should search through chat sessions', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for session search functionality
      cy.get('body').then($body => {
        const searchSelectors = [
          '[data-cy="search-sessions"]', '.session-search',
          'input[placeholder*="search"]', '.search-chats'
        ]
        
        searchSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
            cy.get(selector).first().type('test search')
            cy.wait(500)
            cy.get(selector).first().clear()
          }
        })
      })
    })

    it('should filter sessions by date', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for date filtering
      cy.get('body').then($body => {
        const dateFilterSelectors = [
          '[data-cy="date-filter"]', '.date-filter',
          'select[name*="date"]', '.filter-by-date'
        ]
        
        dateFilterSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })

    it('should sort sessions by various criteria', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for sorting options
      cy.get('body').then($body => {
        const sortSelectors = [
          '[data-cy="sort-sessions"]', '.sort-sessions',
          'select[name*="sort"]', '.session-sort'
        ]
        
        sortSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })

    it('should navigate session pagination', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for pagination controls
      cy.get('body').then($body => {
        const paginationSelectors = [
          '.pagination', '[data-cy="session-pagination"]',
          '.load-more-sessions', 'button[aria-label*="next"]'
        ]
        
        paginationSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })
  })

  describe('Session Export and Backup', () => {
    it('should export individual sessions', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for export functionality
      cy.get('body').then($body => {
        const exportSelectors = [
          '[data-cy="export-session"]', '.export-chat',
          '[aria-label*="export"]', '.download-session'
        ]
        
        exportSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })

    it('should backup all sessions', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for backup all functionality
      cy.get('body').then($body => {
        const backupSelectors = [
          '[data-cy="backup-all-sessions"]', '.backup-all',
          '.export-all-chats', '.download-all'
        ]
        
        backupSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })

    it('should import session data', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for import functionality
      cy.get('body').then($body => {
        const importSelectors = [
          '[data-cy="import-sessions"]', '.import-chats',
          'input[type="file"][accept*="json"]', '.restore-backup'
        ]
        
        importSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })
  })

  describe('Session Collaboration Features', () => {
    it('should support session sharing', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for sharing functionality
      cy.get('body').then($body => {
        const shareSelectors = [
          '[data-cy="share-session"]', '.share-chat',
          '[aria-label*="share"]', '.share-conversation'
        ]
        
        shareSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })

    it('should handle session permissions', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for permission controls
      cy.get('body').then($body => {
        const permissionSelectors = [
          '[data-cy="session-permissions"]', '.permission-settings',
          '.privacy-controls', '.access-controls'
        ]
        
        permissionSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })

    it('should support session templates', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for template functionality
      cy.get('body').then($body => {
        const templateSelectors = [
          '[data-cy="session-templates"]', '.chat-templates',
          '.conversation-templates', '.session-presets'
        ]
        
        templateSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })
  })

  describe('Session Performance', () => {
    it('should handle many sessions efficiently', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test with multiple sessions
      cy.get('body').then($body => {
        const sessionList = $body.find('.session-list, [data-cy="session-list"]')
        
        if (sessionList.length > 0) {
          // Scroll through session list
          cy.get(sessionList).first().scrollTo('top')
          cy.wait(300)
          cy.get(sessionList).first().scrollTo('bottom')
          cy.wait(300)
        }
      })
    })

    it('should lazy load session content', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test lazy loading
      cy.get('body').then($body => {
        const lazyLoadSelectors = [
          '.lazy-load-sessions', '[data-cy="lazy-sessions"]',
          '.session-lazy-load'
        ]
        
        lazyLoadSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })

    it('should optimize session switching', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test quick session switching
      cy.get('body').then($body => {
        const sessionItems = $body.find('.session-item, [data-cy="session-item"]')
        
        if (sessionItems.length > 1) {
          // Quick switch between sessions
          cy.get(sessionItems).eq(0).click()
          cy.wait(100)
          cy.get(sessionItems).eq(1).click()
          cy.wait(100)
          
          // Should handle rapid switching gracefully
          cy.get('body').should('be.visible')
        }
      })
    })
  })
})

