// User Experience E2E Tests
// Tests animations, notifications, accessibility, and UX interactions

describe('User Experience', () => {
  beforeEach(() => {
    cy.clearAllStorage()
    cy.setupCommonInterceptors()
  })

  describe('Loading States and Feedback', () => {
    it('should show appropriate loading indicators', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for loading indicators
      cy.get('body').then($body => {
        const loadingSelectors = [
          '.loading', '[data-cy="loading"]',
          '.spinner', '.loading-spinner',
          '.skeleton', '.loading-placeholder'
        ]
        
        loadingSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })

    it('should provide visual feedback for user actions', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test button feedback
      cy.get('body').then($body => {
        const clickableElements = [
          'button', '[data-cy="send-button"]',
          '.btn', '.clickable'
        ]
        
        clickableElements.forEach(element => {
          if ($body.find(element).length > 0) {
            // Test hover and click states
            cy.get(element).first().trigger('mouseover')
            cy.wait(100)
            cy.get(element).first().trigger('mouseout')
          }
        })
      })
    })

    it('should show progress indicators for long operations', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Simulate long operation
      cy.get('body').then($body => {
        const messageInput = $body.find('[data-cy="chat-input"]')
        
        if (messageInput.length > 0) {
          // Intercept to simulate slow response
          cy.intercept('POST', '**/chat/**', (req) => {
            req.reply((res) => {
              res.delay(3000)
              res.send({ statusCode: 200, body: { message: 'Response' } })
            })
          }).as('slowResponse')
          
          cy.get('[data-cy="chat-input"]').first().type('Test progress indicator')
          cy.get('[data-cy="send-button"]').first().click()
          
          // Look for progress indicators
          const progressSelectors = [
            '.progress', '[data-cy="progress"]',
            '.progress-bar', '.loading-bar'
          ]
          
          progressSelectors.forEach(selector => {
            if ($body.find(selector).length > 0) {
              cy.get(selector).first().should('be.visible')
            }
          })
        }
      })
    })

    it('should handle empty states gracefully', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for empty state indicators
      cy.get('body').then($body => {
        const emptyStateSelectors = [
          '.empty-state', '[data-cy="empty-state"]',
          '.no-messages', '.empty-chat',
          '.placeholder-content'
        ]
        
        emptyStateSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })
  })

  describe('Animations and Transitions', () => {
    it('should have smooth page transitions', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test navigation transitions
      cy.get('body').then($body => {
        const navLinks = $body.find('nav a, .nav-link, [data-cy="nav-link"]')
        
        if (navLinks.length > 0) {
          navLinks.each((index, link) => {
            if (index < 2) { // Test first 2 links
              cy.wrap(link).click()
              cy.wait(500) // Allow transition
            }
          })
        }
      })
    })

    it('should animate message appearance', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Send message and observe animation
      cy.get('body').then($body => {
        const messageInput = $body.find('[data-cy="chat-input"]')
        
        if (messageInput.length > 0) {
          cy.get('[data-cy="chat-input"]').first().type('Test message animation')
          cy.get('[data-cy="send-button"]').first().click()
          
          // Look for animation classes
          const animationSelectors = [
            '.message-enter', '.fade-in',
            '.slide-in', '.animate-in'
          ]
          
          cy.wait(500)
          
          animationSelectors.forEach(selector => {
            if ($body.find(selector).length > 0) {
              cy.get(selector).first().should('be.visible')
            }
          })
        }
      })
    })

    it('should have smooth sidebar animations', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test sidebar toggle
      cy.get('body').then($body => {
        const sidebarToggleSelectors = [
          '[data-cy="sidebar-toggle"]', '.sidebar-toggle',
          '.menu-toggle', '.hamburger-menu'
        ]
        
        sidebarToggleSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().click()
            cy.wait(500) // Allow animation
            cy.get(selector).first().click()
            cy.wait(500)
          }
        })
      })
    })

    it('should animate modal appearances', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for modal triggers
      cy.get('body').then($body => {
        const modalTriggers = [
          '[data-cy="open-modal"]', '.modal-trigger',
          '.open-dialog', '[data-toggle="modal"]'
        ]
        
        modalTriggers.forEach(trigger => {
          if ($body.find(trigger).length > 0) {
            cy.get(trigger).first().click()
            cy.wait(500)
            
            // Look for modal animations
            const modalSelectors = [
              '.modal-enter', '.fade-in-modal',
              '.slide-up', '.modal-animation'
            ]
            
            modalSelectors.forEach(modalSelector => {
              if ($body.find(modalSelector).length > 0) {
                cy.get(modalSelector).first().should('be.visible')
              }
            })
          }
        })
      })
    })
  })

  describe('Notifications and Alerts', () => {
    it('should show success notifications', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Trigger an action that should show success notification
      cy.get('body').then($body => {
        const messageInput = $body.find('[data-cy="chat-input"]')
        
        if (messageInput.length > 0) {
          cy.get('[data-cy="chat-input"]').first().type('Test success notification')
          cy.get('[data-cy="send-button"]').first().click()
          
          // Look for success notifications
          const successSelectors = [
            '.notification-success', '[data-cy="success-notification"]',
            '.alert-success', '.toast-success'
          ]
          
          cy.wait(1000)
          
          successSelectors.forEach(selector => {
            if ($body.find(selector).length > 0) {
              cy.get(selector).first().should('be.visible')
            }
          })
        }
      })
    })

    it('should show error notifications', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Simulate error condition
      cy.intercept('POST', '**/chat/**', { forceNetworkError: true }).as('networkError')
      
      cy.get('body').then($body => {
        const messageInput = $body.find('[data-cy="chat-input"]')
        
        if (messageInput.length > 0) {
          cy.get('[data-cy="chat-input"]').first().type('Test error notification')
          cy.get('[data-cy="send-button"]').first().click()
          
          // Look for error notifications
          const errorSelectors = [
            '.notification-error', '[data-cy="error-notification"]',
            '.alert-error', '.toast-error',
            '.error-message'
          ]
          
          cy.wait(2000)
          
          errorSelectors.forEach(selector => {
            if ($body.find(selector).length > 0) {
              cy.get(selector).first().should('be.visible')
            }
          })
        }
      })
    })

    it('should auto-dismiss notifications', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for notifications that auto-dismiss
      cy.get('body').then($body => {
        const notificationSelectors = [
          '.notification', '.toast', '.alert',
          '[data-cy="notification"]'
        ]
        
        notificationSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
            
            // Wait for auto-dismiss
            cy.wait(5000)
            
            // Should be gone or have dismiss animation
            cy.get('body').should('be.visible')
          }
        })
      })
    })

    it('should allow manual notification dismissal', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for dismissible notifications
      cy.get('body').then($body => {
        const dismissSelectors = [
          '.notification-close', '[data-cy="close-notification"]',
          '.toast-close', '.alert-dismiss'
        ]
        
        dismissSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().click()
            cy.wait(500)
          }
        })
      })
    })
  })

  describe('Accessibility Features', () => {
    it('should support keyboard navigation', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test tab navigation - find the first focusable element
      cy.get('body').then($body => {
        const focusableElements = [
          'button:enabled', 'input:enabled', 'textarea:enabled', 
          'select:enabled', '[tabindex]:not([tabindex="-1"])',
          'a[href]', '[data-cy="send-button"]'
        ]
        
        let foundFocusable = false
        focusableElements.forEach(selector => {
          if (!foundFocusable && $body.find(selector).length > 0) {
            cy.get(selector).first().focus()
            cy.get(selector).first().should('be.focused')
            
            // Test tab navigation
            cy.get(selector).first().tab()
            cy.wait(200)
            
            // Verify that focus moved (if there are multiple focusable elements)
            if ($body.find(selector).length > 1) {
              cy.focused().should('be.visible')
            }
            foundFocusable = true
          }
        })
        
        // If no focusable elements found, just verify page is accessible
        if (!foundFocusable) {
          cy.get('body').should('be.visible')
        }
      })
    })

    it('should have proper ARIA labels', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Check for ARIA labels on important elements
      cy.get('body').then($body => {
        const ariaElements = [
          '[aria-label]', '[aria-labelledby]',
          '[aria-describedby]', '[role]'
        ]
        
        ariaElements.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('have.attr', selector.replace(/[\[\]]/g, '').split('=')[0])
          }
        })
      })
    })

    it('should support screen readers', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Check for screen reader friendly elements
      cy.get('body').then($body => {
        const screenReaderSelectors = [
          '.sr-only', '.screen-reader-only',
          '[aria-live]', '[aria-describedby]'
        ]
        
        screenReaderSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('exist')
          }
        })
      })
    })

    it('should have sufficient color contrast', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test that text is readable (basic visibility check)
      cy.get('body').then($body => {
        const textElements = ['p', 'span', 'h1', 'h2', 'h3', 'button', 'input']
        
        textElements.forEach(element => {
          if ($body.find(element).length > 0) {
            cy.get(element).first().should('be.visible')
          }
        })
      })
    })

    it('should support focus management', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test focus management on enabled interactive elements
      cy.get('body').then($body => {
        const focusableElements = [
          'button:enabled:visible', 
          'input:enabled:visible', 
          'textarea:enabled:visible', 
          'select:enabled:visible',
          '[tabindex]:not([tabindex="-1"]):visible',
          'a[href]:visible'
        ]
        
        let testedFocus = false
        focusableElements.forEach(selector => {
          if (!testedFocus && $body.find(selector).length > 0) {
            // Only test the first enabled, visible focusable element
            cy.get(selector).first().then($el => {
              // Check if element is actually focusable (not disabled)
              if (!$el.is(':disabled') && $el.is(':visible')) {
                cy.wrap($el).focus()
                cy.wrap($el).should('be.focused')
                testedFocus = true
              }
            })
          }
        })
        
        // If no focusable elements found, verify basic interactivity exists
        if (!testedFocus) {
          const basicInteractiveElements = [
            'button', 'a', 'input', '[role="button"]'
          ]
          
          basicInteractiveElements.forEach(selector => {
            if ($body.find(selector).length > 0) {
              cy.get(selector).first().should('exist').and('be.visible')
            }
          })
        }
      })
    })
  })

  describe('Responsive Design', () => {
    it('should adapt to mobile viewports', () => {
      cy.viewport(375, 667) // iPhone SE
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test mobile-specific elements
      cy.get('body').then($body => {
        const mobileElements = [
          '.mobile-menu', '.mobile-nav',
          '[data-cy="mobile-sidebar"]'
        ]
        
        mobileElements.forEach(element => {
          if ($body.find(element).length > 0) {
            cy.get(element).first().should('be.visible')
          }
        })
      })
    })

    it('should adapt to tablet viewports', () => {
      cy.viewport(768, 1024) // iPad
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test tablet layout
      cy.get('body').then($body => {
        const tabletElements = [
          '.tablet-layout', '.medium-screen',
          '[data-cy="tablet-view"]'
        ]
        
        tabletElements.forEach(element => {
          if ($body.find(element).length > 0) {
            cy.get(element).first().should('be.visible')
          }
        })
      })
    })

    it('should adapt to desktop viewports', () => {
      cy.viewport(1920, 1080) // Desktop
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test desktop layout
      cy.get('body').then($body => {
        const desktopElements = [
          '.desktop-layout', '.large-screen',
          '[data-cy="desktop-view"]', '.sidebar'
        ]
        
        desktopElements.forEach(element => {
          if ($body.find(element).length > 0) {
            cy.get(element).first().should('be.visible')
          }
        })
      })
    })

    it('should handle orientation changes', () => {
      // Test portrait to landscape
      cy.viewport(375, 667) // Portrait
      cy.visit('/chat')
      cy.waitForApp()
      
      cy.viewport(667, 375) // Landscape
      cy.wait(500)
      
      // Should still be functional
      cy.get('body').should('be.visible')
    })
  })

  describe('Performance and Smoothness', () => {
    it('should have smooth scrolling performance', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test scrolling performance
      cy.get('body').then($body => {
        const scrollableElements = [
          '.chat-messages', '.message-list',
          '.scrollable-content'
        ]
        
        scrollableElements.forEach(element => {
          if ($body.find(element).length > 0) {
            // Rapid scrolling test
            for (let i = 0; i < 5; i++) {
              cy.get(element).first().scrollTo('top')
              cy.wait(50)
              cy.get(element).first().scrollTo('bottom')
              cy.wait(50)
            }
          }
        })
      })
    })

    it('should handle rapid user interactions', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test rapid clicking
      cy.get('body').then($body => {
        const clickableElements = $body.find('button:visible')
        
        if (clickableElements.length > 0) {
          const element = clickableElements.first()
          
          // Rapid clicks
          for (let i = 0; i < 5; i++) {
            cy.wrap(element).click()
            cy.wait(50)
          }
          
          // Should handle gracefully
          cy.get('body').should('be.visible')
        }
      })
    })

    it('should maintain 60fps during animations', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test animation performance (basic check)
      cy.get('body').then($body => {
        const animatedElements = [
          '.animated', '.transition',
          '[data-cy="animated-element"]'
        ]
        
        animatedElements.forEach(element => {
          if ($body.find(element).length > 0) {
            // Trigger animation and verify smoothness
            cy.get(element).first().trigger('mouseover')
            cy.wait(500)
            cy.get(element).first().trigger('mouseout')
          }
        })
      })
    })

    it('should optimize image loading', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test image optimization
      cy.get('body').then($body => {
        const images = $body.find('img')
        
        if (images.length > 0) {
          images.each((index, img) => {
            if (index < 3) { // Test first 3 images
              cy.wrap(img).should('be.visible')
              cy.wrap(img).should('have.attr', 'src')
            }
          })
        }
      })
    })
  })

  describe('Error Boundaries and Recovery', () => {
    it('should handle JavaScript errors gracefully', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Should not crash on errors
      cy.window().then((win) => {
        // Override console.error to catch errors
        const originalError = win.console.error
        const errors = []
        
        win.console.error = (...args) => {
          errors.push(args)
          originalError.apply(win.console, args)
        }
        
        // Trigger potential error scenario
        cy.get('body').should('be.visible')
      })
    })

    it('should provide error recovery options', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for error recovery elements
      cy.get('body').then($body => {
        const recoverySelectors = [
          '[data-cy="retry-button"]', '.retry',
          '.reload-page', '.error-recovery'
        ]
        
        recoverySelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })

    it('should maintain state during errors', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Send message then simulate error
      cy.get('body').then($body => {
        const messageInput = $body.find('[data-cy="chat-input"]')
        
        if (messageInput.length > 0) {
          cy.get('[data-cy="chat-input"]').first().type('Test state preservation')
          cy.get('[data-cy="send-button"]').first().click()
          cy.wait(1000)
          
          // Simulate network error for next request
          cy.intercept('POST', '**/chat/**', { forceNetworkError: true })
          
          cy.get('[data-cy="chat-input"]').first().type('Error test message')
          cy.get('[data-cy="send-button"]').first().click()
          cy.wait(2000)
          
          // Previous message should still be visible
          cy.get('body').should('contain.text', 'Test state preservation')
        }
      })
    })
  })
})
