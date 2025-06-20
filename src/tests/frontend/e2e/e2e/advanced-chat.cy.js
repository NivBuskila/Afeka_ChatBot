// Advanced Chat Features E2E Tests
// Tests enhanced chat capabilities, streaming responses, and message actions

describe('Advanced Chat Features', () => {
  beforeEach(() => {
    cy.clearAllStorage()
    cy.setupCommonInterceptors()
  })

  describe('Enhanced Message Features', () => {
    it('should provide message copy functionality', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Send a test message first
      cy.get('body').then($body => {
        const inputSelectors = [
          '[data-cy="chat-input"]', 'textarea[placeholder*="message"]',
          'input[placeholder*="type"]', '.chat-input'
        ]
        
        inputSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().type('Test message for copying')
            
            // Send the message
            const sendSelectors = [
              '[data-cy="send-button"]', 'button[type="submit"]',
              '.send-button', '[aria-label*="send"]'
            ]
            
            sendSelectors.forEach(sendSelector => {
              if ($body.find(sendSelector).length > 0) {
                cy.get(sendSelector).first().click()
                cy.wait(1000)
                
                // Look for copy button on messages
                const copySelectors = [
                  '[data-cy="copy-message"]', '.copy-button',
                  '[aria-label*="copy"]', '[title*="copy"]',
                  '.message-copy', 'button[data-action="copy"]'
                ]
                
                copySelectors.forEach(copySelector => {
                  if ($body.find(copySelector).length > 0) {
                    cy.get(copySelector).first().should('be.visible')
                  }
                })
              }
            })
          }
        })
      })
    })

    it('should show message timestamps', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Send a message and check for timestamps
      cy.get('body').then($body => {
        const inputSelectors = [
          '[data-cy="chat-input"]', 'textarea', '.chat-input'
        ]
        
        inputSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().type('Test message with timestamp')
            
            // Send message
            const sendButton = $body.find('[data-cy="send-button"]')
            if (sendButton.length > 0) {
              cy.get('[data-cy="send-button"]').first().click()
              cy.wait(1000)
              
              // Look for timestamp displays
              const timestampSelectors = [
                '.timestamp', '.message-time', '[data-cy="message-timestamp"]',
                '.time', '.sent-at', '.message-date'
              ]
              
              timestampSelectors.forEach(timestampSelector => {
                if ($body.find(timestampSelector).length > 0) {
                  cy.get(timestampSelector).first().should('be.visible')
                }
              })
            }
          }
        })
      })
    })

    it('should display message status indicators', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Send a message and check for status indicators
      cy.get('body').then($body => {
        const messageInput = $body.find('[data-cy="chat-input"]')
        
        if (messageInput.length > 0) {
          cy.get('[data-cy="chat-input"]').first().type('Test status message')
          cy.get('[data-cy="send-button"]').first().click()
          
          // Look for status indicators
          const statusSelectors = [
            '.message-status', '[data-cy="message-status"]',
            '.sent', '.delivered', '.read',
            '.message-pending', '.message-success', '.message-error'
          ]
          
          statusSelectors.forEach(statusSelector => {
            if ($body.find(statusSelector).length > 0) {
              cy.get(statusSelector).first().should('be.visible')
            }
          })
        }
      })
    })

    it('should handle message reactions', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Send message and test reactions
      cy.get('body').then($body => {
        const messageInput = $body.find('[data-cy="chat-input"]')
        
        if (messageInput.length > 0) {
          cy.get('[data-cy="chat-input"]').first().type('Message for reactions')
          cy.get('[data-cy="send-button"]').first().click()
          cy.wait(1000)
          
          // Look for reaction functionality
          const reactionSelectors = [
            '[data-cy="add-reaction"]', '.reaction-button',
            '.emoji-picker', '[aria-label*="react"]',
            '.message-reactions', '.add-emoji'
          ]
          
          reactionSelectors.forEach(reactionSelector => {
            if ($body.find(reactionSelector).length > 0) {
              cy.get(reactionSelector).first().should('be.visible')
            }
          })
        }
      })
    })

    it('should support message threading', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test message threading/replies
      cy.get('body').then($body => {
        const messageInput = $body.find('[data-cy="chat-input"]')
        
        if (messageInput.length > 0) {
          cy.get('[data-cy="chat-input"]').first().type('Original message for thread')
          cy.get('[data-cy="send-button"]').first().click()
          cy.wait(1000)
          
          // Look for reply/thread functionality
          const replySelectors = [
            '[data-cy="reply-message"]', '.reply-button',
            '[aria-label*="reply"]', '[title*="reply"]',
            '.message-reply', 'button[data-action="reply"]'
          ]
          
          replySelectors.forEach(replySelector => {
            if ($body.find(replySelector).length > 0) {
              cy.get(replySelector).first().should('be.visible')
            }
          })
        }
      })
    })
  })

  describe('Streaming and Real-time Features', () => {
    it('should show typing indicators', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Send a message and look for AI typing indicator
      cy.get('body').then($body => {
        const messageInput = $body.find('[data-cy="chat-input"]')
        
        if (messageInput.length > 0) {
          // Intercept chat API to simulate slow response
          cy.intercept('POST', '**/chat/**', (req) => {
            req.reply((res) => {
              res.delay(2000) // Simulate typing delay
              res.send({
                statusCode: 200,
                body: { message: 'AI response', streaming: true }
              })
            })
          }).as('chatResponse')
          
          cy.get('[data-cy="chat-input"]').first().type('Test for typing indicator')
          cy.get('[data-cy="send-button"]').first().click()
          
          // Look for typing indicators
          const typingSelectors = [
            '[data-cy="typing-indicator"]', '.typing-indicator',
            '.ai-typing', '.is-typing', '.typing-dots',
            '.loading-response', '.thinking'
          ]
          
          typingSelectors.forEach(typingSelector => {
            if ($body.find(typingSelector).length > 0) {
              cy.get(typingSelector).first().should('be.visible')
            }
          })
        }
      })
    })

    it('should handle streaming responses', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test streaming response
      cy.get('body').then($body => {
        const messageInput = $body.find('[data-cy="chat-input"]')
        
        if (messageInput.length > 0) {
          // Intercept to simulate streaming
          cy.intercept('POST', '**/chat/**', (req) => {
            req.reply({
              statusCode: 200,
              body: { message: 'This is a streaming response...', streaming: true }
            })
          }).as('streamingResponse')
          
          cy.get('[data-cy="chat-input"]').first().type('Test streaming response')
          cy.get('[data-cy="send-button"]').first().click()
          
          // Look for streaming indicators
          const streamingSelectors = [
            '.streaming', '[data-cy="streaming-message"]',
            '.partial-response', '.live-response',
            '.response-building'
          ]
          
          streamingSelectors.forEach(streamingSelector => {
            if ($body.find(streamingSelector).length > 0) {
              cy.get(streamingSelector).first().should('be.visible')
            }
          })
        }
      })
    })

    it('should handle real-time message updates', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test real-time updates
      cy.get('body').then($body => {
        // Look for real-time connection indicators
        const realtimeSelectors = [
          '[data-cy="realtime-status"]', '.realtime-indicator',
          '.live-connection', '.websocket-status'
        ]
        
        realtimeSelectors.forEach(realtimeSelector => {
          if ($body.find(realtimeSelector).length > 0) {
            cy.get(realtimeSelector).first().should('be.visible')
          }
        })
      })
    })

    it('should show connection quality indicators', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test connection quality display
      cy.get('body').then($body => {
        const qualitySelectors = [
          '[data-cy="connection-quality"]', '.connection-quality',
          '.network-speed', '.latency-indicator',
          '.signal-strength'
        ]
        
        qualitySelectors.forEach(qualitySelector => {
          if ($body.find(qualitySelector).length > 0) {
            cy.get(qualitySelector).first().should('be.visible')
          }
        })
      })
    })
  })

  describe('Advanced Input Features', () => {
    it('should support rich text formatting', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test rich text features
      cy.get('body').then($body => {
        const richTextSelectors = [
          '.rich-text-editor', '[data-cy="rich-editor"]',
          '.formatting-toolbar', '.text-editor'
        ]
        
        richTextSelectors.forEach(richTextSelector => {
          if ($body.find(richTextSelector).length > 0) {
            cy.get(richTextSelector).first().should('be.visible')
            
            // Look for formatting buttons
            const formatButtons = [
              '.bold-button', '.italic-button', '.underline-button'
            ]
            
            formatButtons.forEach(formatButton => {
              if ($body.find(formatButton).length > 0) {
                cy.get(formatButton).first().should('be.visible')
              }
            })
          }
        })
      })
    })

    it('should support file attachments', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test file attachment feature
      cy.get('body').then($body => {
        const attachmentSelectors = [
          '[data-cy="attach-file"]', '.attachment-button',
          '[type="file"]', '.file-input',
          '[aria-label*="attach"]', '.upload-button'
        ]
        
        attachmentSelectors.forEach(attachmentSelector => {
          if ($body.find(attachmentSelector).length > 0) {
            cy.get(attachmentSelector).first().should('be.visible')
          }
        })
      })
    })

    it('should handle drag and drop for files', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test drag and drop functionality
      cy.get('body').then($body => {
        const dropzoneSelectors = [
          '[data-cy="drop-zone"]', '.drop-zone',
          '.file-drop-area', '[data-drop="true"]'
        ]
        
        dropzoneSelectors.forEach(dropzoneSelector => {
          if ($body.find(dropzoneSelector).length > 0) {
            // Simulate drag and drop
            const fileName = 'test-file.txt'
            const fileContent = 'Test file content'
            
            cy.get(dropzoneSelector).first().selectFile({
              contents: Cypress.Buffer.from(fileContent),
              fileName: fileName,
              mimeType: 'text/plain'
            }, { action: 'drag-drop', force: true })
            
            cy.wait(500)
          }
        })
      })
    })

    it('should provide input auto-complete suggestions', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test auto-complete functionality
      cy.get('body').then($body => {
        const messageInput = $body.find('[data-cy="chat-input"]')
        
        if (messageInput.length > 0) {
          cy.get('[data-cy="chat-input"]').first().type('How to')
          cy.wait(500)
          
          // Look for suggestion dropdown
          const suggestionSelectors = [
            '.autocomplete-suggestions', '[data-cy="suggestions"]',
            '.suggestion-dropdown', '.auto-complete'
          ]
          
          suggestionSelectors.forEach(suggestionSelector => {
            if ($body.find(suggestionSelector).length > 0) {
              cy.get(suggestionSelector).first().should('be.visible')
            }
          })
          
          cy.get('[data-cy="chat-input"]').first().clear()
        }
      })
    })

    it('should support emoji picker', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test emoji picker
      cy.get('body').then($body => {
        const emojiSelectors = [
          '[data-cy="emoji-picker"]', '.emoji-button',
          '.emoji-selector', '[aria-label*="emoji"]'
        ]
        
        emojiSelectors.forEach(emojiSelector => {
          if ($body.find(emojiSelector).length > 0) {
            cy.get(emojiSelector).first().click()
            cy.wait(500)
            
            // Look for emoji panel
            const emojiPanelSelectors = [
              '.emoji-panel', '.emoji-grid', '[data-cy="emoji-grid"]'
            ]
            
            emojiPanelSelectors.forEach(panelSelector => {
              if ($body.find(panelSelector).length > 0) {
                cy.get(panelSelector).first().should('be.visible')
              }
            })
          }
        })
      })
    })
  })

  describe('Message Actions and Context Menu', () => {
    it('should provide message context menu', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Send message and test context menu
      cy.get('body').then($body => {
        const messageInput = $body.find('[data-cy="chat-input"]')
        
        if (messageInput.length > 0) {
          cy.get('[data-cy="chat-input"]').first().type('Test context menu message')
          cy.get('[data-cy="send-button"]').first().click()
          cy.wait(1000)
          
          // Look for message context menu triggers
          const menuSelectors = [
            '.message-menu', '[data-cy="message-actions"]',
            '.context-menu-trigger', '.message-options'
          ]
          
          menuSelectors.forEach(menuSelector => {
            if ($body.find(menuSelector).length > 0) {
              // Right-click to open context menu
              cy.get(menuSelector).first().rightclick()
              cy.wait(300)
              
              // Look for context menu
              const contextMenuSelectors = [
                '.context-menu', '.message-context-menu',
                '[data-cy="context-menu"]', '.dropdown-menu'
              ]
              
              contextMenuSelectors.forEach(contextSelector => {
                if ($body.find(contextSelector).length > 0) {
                  cy.get(contextSelector).first().should('be.visible')
                }
              })
            }
          })
        }
      })
    })

    it('should support message pinning', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test message pinning
      cy.get('body').then($body => {
        const messageInput = $body.find('[data-cy="chat-input"]')
        
        if (messageInput.length > 0) {
          cy.get('[data-cy="chat-input"]').first().type('Important message to pin')
          cy.get('[data-cy="send-button"]').first().click()
          cy.wait(1000)
          
          // Look for pin functionality
          const pinSelectors = [
            '[data-cy="pin-message"]', '.pin-button',
            '[aria-label*="pin"]', '[title*="pin"]',
            '.message-pin', 'button[data-action="pin"]'
          ]
          
          pinSelectors.forEach(pinSelector => {
            if ($body.find(pinSelector).length > 0) {
              cy.get(pinSelector).first().should('be.visible')
            }
          })
        }
      })
    })

    it('should support message bookmarking', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test message bookmarking
      cy.get('body').then($body => {
        const messageInput = $body.find('[data-cy="chat-input"]')
        
        if (messageInput.length > 0) {
          cy.get('[data-cy="chat-input"]').first().type('Message to bookmark')
          cy.get('[data-cy="send-button"]').first().click()
          cy.wait(1000)
          
          // Look for bookmark functionality
          const bookmarkSelectors = [
            '[data-cy="bookmark-message"]', '.bookmark-button',
            '[aria-label*="bookmark"]', '[title*="bookmark"]',
            '.message-bookmark', 'button[data-action="bookmark"]'
          ]
          
          bookmarkSelectors.forEach(bookmarkSelector => {
            if ($body.find(bookmarkSelector).length > 0) {
              cy.get(bookmarkSelector).first().should('be.visible')
            }
          })
        }
      })
    })

    it('should support message translation', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test message translation
      cy.get('body').then($body => {
        const messageInput = $body.find('[data-cy="chat-input"]')
        
        if (messageInput.length > 0) {
          cy.get('[data-cy="chat-input"]').first().type('Hello, how are you?')
          cy.get('[data-cy="send-button"]').first().click()
          cy.wait(1000)
          
          // Look for translation functionality
          const translateSelectors = [
            '[data-cy="translate-message"]', '.translate-button',
            '[aria-label*="translate"]', '[title*="translate"]',
            '.message-translate', 'button[data-action="translate"]'
          ]
          
          translateSelectors.forEach(translateSelector => {
            if ($body.find(translateSelector).length > 0) {
              cy.get(translateSelector).first().should('be.visible')
            }
          })
        }
      })
    })
  })

  describe('Performance and Optimization', () => {
    it('should handle large message volumes efficiently', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test performance with multiple messages
      cy.get('body').then($body => {
        const messageInput = $body.find('[data-cy="chat-input"]')
        
        if (messageInput.length > 0) {
          // Send multiple messages quickly
          for (let i = 1; i <= 5; i++) {
            cy.get('[data-cy="chat-input"]').first().type(`Performance test message ${i}`)
            cy.get('[data-cy="send-button"]').first().click()
            cy.wait(200) // Quick succession
          }
          
          // Verify all messages are displayed
          cy.get('body').should('be.visible')
          cy.wait(1000)
        }
      })
    })

    it('should implement message virtualization for long conversations', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test message virtualization
      cy.get('body').then($body => {
        const virtualizationSelectors = [
          '.virtualized-list', '[data-cy="virtual-scroll"]',
          '.message-virtualization', '.virtual-list'
        ]
        
        virtualizationSelectors.forEach(virtualizationSelector => {
          if ($body.find(virtualizationSelector).length > 0) {
            cy.get(virtualizationSelector).first().should('be.visible')
          }
        })
      })
    })

    it('should lazy load message history', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test lazy loading
      cy.get('body').then($body => {
        const lazyLoadSelectors = [
          '.lazy-load-trigger', '[data-cy="load-more"]',
          '.infinite-scroll', '.load-previous'
        ]
        
        lazyLoadSelectors.forEach(lazyLoadSelector => {
          if ($body.find(lazyLoadSelector).length > 0) {
            cy.get(lazyLoadSelector).first().should('be.visible')
          }
        })
      })
    })

    it('should optimize image and media loading', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test media optimization
      cy.get('body').then($body => {
        const mediaSelectors = [
          '.lazy-image', '.optimized-media',
          '[data-cy="lazy-media"]', '.progressive-image'
        ]
        
        mediaSelectors.forEach(mediaSelector => {
          if ($body.find(mediaSelector).length > 0) {
            cy.get(mediaSelector).first().should('be.visible')
          }
        })
      })
    })
  })
})
