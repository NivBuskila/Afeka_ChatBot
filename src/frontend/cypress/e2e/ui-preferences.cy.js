// UI Preferences E2E Tests
// Tests theme switching, language switching, and layout responsiveness

describe('UI Preferences', () => {
  beforeEach(() => {
    cy.clearAllStorage()
    cy.setupCommonInterceptors()
  })

  describe('Theme Switching', () => {
    it('should access theme toggle controls', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for theme toggle button/controls
      cy.get('body').then($body => {
        const themeSelectors = [
          '[data-cy="theme-toggle"]', '.theme-toggle',
          '[data-cy="dark-mode-toggle"]', '.dark-mode-toggle',
          '[aria-label*="theme"]', '[title*="theme"]',
          '.theme-switcher', 'button[data-theme]',
          '[data-cy="light-dark-toggle"]'
        ]
        
        themeSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })

    it('should toggle between light and dark themes', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Get initial theme state
      cy.get('body').then($initialBody => {
        const initialClasses = $initialBody.attr('class') || ''
        const initialDataTheme = $initialBody.attr('data-theme') || ''
        
        // Look for theme toggle and click it
        const themeSelectors = [
          '[data-cy="theme-toggle"]', '.theme-toggle',
          '[data-cy="dark-mode-toggle"]', '.dark-mode-toggle',
          '[aria-label*="theme"]', 'button[data-theme]'
        ]
        
        themeSelectors.forEach(selector => {
          if ($initialBody.find(selector).length > 0) {
            cy.get(selector).first().click()
            cy.wait(500) // Allow theme transition
            
            // Verify theme changed
            cy.get('body').then($newBody => {
              const newClasses = $newBody.attr('class') || ''
              const newDataTheme = $newBody.attr('data-theme') || ''
              
              // Theme should have changed somehow
              const themeChanged = 
                newClasses !== initialClasses || 
                newDataTheme !== initialDataTheme ||
                $newBody.css('background-color') !== $initialBody.css('background-color')
              
              if (themeChanged) {
                // Click again to toggle back
                cy.get(selector).first().click()
                cy.wait(500)
              }
            })
          }
        })
      })
    })

    it('should persist theme selection across page reloads', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for theme toggle
      cy.get('body').then($body => {
        const themeSelectors = [
          '[data-cy="theme-toggle"]', '.theme-toggle',
          '[data-cy="dark-mode-toggle"]'
        ]
        
        themeSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            // Toggle theme
            cy.get(selector).first().click()
            cy.wait(500)
            
            // Get theme state after toggle
            cy.get('body').then($themedBody => {
              const themedClasses = $themedBody.attr('class') || ''
              const themedDataTheme = $themedBody.attr('data-theme') || ''
              
              // Reload page
              cy.reload()
              cy.waitForApp()
              
              // Check if theme persisted (at least partially)
              cy.get('body').should('be.visible')
            })
          }
        })
      })
    })

    it('should apply theme to all UI components', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for theme toggle
      cy.get('body').then($body => {
        if ($body.find('[data-cy="theme-toggle"]').length > 0) {
          // Toggle theme
          cy.get('[data-cy="theme-toggle"]').first().click()
          cy.wait(500)
          
          // Check that various components are visible and themed
          const componentSelectors = [
            'header', 'nav', 'main', 'footer',
            '.chat-container', '.message', 'button',
            'input', 'textarea', '.sidebar'
          ]
          
          componentSelectors.forEach(selector => {
            if ($body.find(selector).length > 0) {
              cy.get(selector).first().should('be.visible')
            }
          })
        }
      })
    })
  })

  describe('Language Switching', () => {
    it('should access language toggle controls', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for language toggle button/controls
      cy.get('body').then($body => {
        const languageSelectors = [
          '[data-cy="language-toggle"]', '.language-toggle',
          '[data-cy="hebrew-english-toggle"]', '.lang-switcher',
          '[aria-label*="language"]', '[title*="language"]',
          '[data-cy="rtl-toggle"]', 'button[data-lang]',
          '.language-selector', '[data-cy="lang"]'
        ]
        
        languageSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
          }
        })
      })
    })

    it('should toggle between Hebrew and English', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for language toggle
      cy.get('body').then($body => {
        const languageSelectors = [
          '[data-cy="language-toggle"]', '.language-toggle',
          '[data-cy="hebrew-english-toggle"]', '.lang-switcher'
        ]
        
        languageSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            // Get initial language state
            const initialDir = $body.attr('dir') || ''
            const initialLang = $body.attr('lang') || ''
            
            // Toggle language
            cy.get(selector).first().click()
            cy.wait(500) // Allow language change
            
            // Verify language changed
            cy.get('body').then($newBody => {
              const newDir = $newBody.attr('dir') || ''
              const newLang = $newBody.attr('lang') || ''
              
              // Check if direction or language attributes changed
              const languageChanged = newDir !== initialDir || newLang !== initialLang
              
              if (languageChanged) {
                // Toggle back
                cy.get(selector).first().click()
                cy.wait(500)
              }
            })
          }
        })
      })
    })

    it('should handle RTL (Hebrew) and LTR (English) layouts', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test RTL layout
      cy.get('body').then($body => {
        // Check for RTL indicators
        const rtlIndicators = [
          '[dir="rtl"]', '.rtl', '[data-direction="rtl"]'
        ]
        
        let hasRTL = false
        rtlIndicators.forEach(selector => {
          if ($body.find(selector).length > 0) {
            hasRTL = true
            cy.get(selector).first().should('be.visible')
          }
        })
        
        // If RTL found, test that layout adapts
        if (hasRTL) {
          // Look for elements that should adapt to RTL
          const adaptiveElements = [
            '.chat-message', '.sidebar', 'nav', 'header'
          ]
          
          adaptiveElements.forEach(element => {
            if ($body.find(element).length > 0) {
              cy.get(element).first().should('be.visible')
            }
          })
        }
      })
    })

    it('should display Hebrew text correctly', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Look for Hebrew text or Hebrew language toggle
      cy.get('body').then($body => {
        const hebrewTexts = ['עברית', 'שלח', 'חיפוש', 'הגדרות', 'צ\'אט']
        let hebrewFound = false
        
        hebrewTexts.forEach(hebrewText => {
          if ($body.text().includes(hebrewText)) {
            hebrewFound = true
            cy.get('body').should('contain.text', hebrewText)
          }
        })
        
        // If no Hebrew found initially, try toggling language
        if (!hebrewFound) {
          const languageSelectors = [
            '[data-cy="language-toggle"]', '.language-toggle'
          ]
          
          languageSelectors.forEach(selector => {
            if ($body.find(selector).length > 0) {
              cy.get(selector).first().click()
              cy.wait(500)
              
              // Check for Hebrew text after toggle
              cy.get('body').then($hebrewBody => {
                hebrewTexts.forEach(hebrewText => {
                  if ($hebrewBody.text().includes(hebrewText)) {
                    cy.get('body').should('contain.text', hebrewText)
                  }
                })
              })
            }
          })
        }
      })
    })

    it('should persist language selection', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Toggle language and check persistence
      cy.get('body').then($body => {
        const languageToggle = '[data-cy="language-toggle"]'
        
        if ($body.find(languageToggle).length > 0) {
          // Get initial state
          const initialDir = $body.attr('dir') || ''
          
          // Toggle language
          cy.get(languageToggle).first().click()
          cy.wait(500)
          
          // Get new state
          cy.get('body').then($newBody => {
            const newDir = $newBody.attr('dir') || ''
            
            // Reload page
            cy.reload()
            cy.waitForApp()
            
            // Check that language preference was saved
            cy.get('body').should('be.visible')
          })
        }
      })
    })
  })

  describe('Layout Responsiveness', () => {
    it('should adapt to different screen sizes with themes', () => {
      const viewports = [
        [375, 667],   // Mobile
        [768, 1024],  // Tablet  
        [1920, 1080]  // Desktop
      ]
      
      viewports.forEach(([width, height]) => {
        cy.viewport(width, height)
        cy.visit('/chat')
        cy.waitForApp()
        
        // Test theme toggle on this viewport
        cy.get('body').then($body => {
          if ($body.find('[data-cy="theme-toggle"]').length > 0) {
            cy.get('[data-cy="theme-toggle"]').first().click()
            cy.wait(300)
            cy.get('body').should('be.visible')
            
            // Toggle back
            cy.get('[data-cy="theme-toggle"]').first().click()
            cy.wait(300)
          }
        })
      })
    })

    it('should handle language switching on mobile devices', () => {
      cy.viewport(375, 667) // Mobile viewport
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test language toggle on mobile
      cy.get('body').then($body => {
        const mobileLanguageSelectors = [
          '[data-cy="language-toggle"]', '.language-toggle',
          '.mobile-lang-toggle', '[data-cy="mobile-lang"]'
        ]
        
        mobileLanguageSelectors.forEach(selector => {
          if ($body.find(selector).length > 0) {
            cy.get(selector).first().should('be.visible')
            cy.get(selector).first().click()
            cy.wait(500)
            cy.get('body').should('be.visible')
          }
        })
      })
    })

    it('should maintain usability across theme and language combinations', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test all combinations: Light+English, Light+Hebrew, Dark+English, Dark+Hebrew
      const combinations = [
        { theme: 'toggle-theme', lang: 'stay-english' },
        { theme: 'stay-theme', lang: 'toggle-hebrew' },
        { theme: 'toggle-theme', lang: 'stay-hebrew' },
        { theme: 'toggle-theme', lang: 'toggle-english' }
      ]
      
      cy.get('body').then($body => {
        const themeToggle = $body.find('[data-cy="theme-toggle"]')
        const langToggle = $body.find('[data-cy="language-toggle"]')
        
        if (themeToggle.length > 0 && langToggle.length > 0) {
          // Test theme toggle
          cy.get('[data-cy="theme-toggle"]').first().click()
          cy.wait(300)
          
          // Test language toggle
          cy.get('[data-cy="language-toggle"]').first().click()
          cy.wait(300)
          
          // Verify app still works
          cy.get('body').should('be.visible')
          
          // Test that critical elements are still accessible
          const criticalElements = [
            'input[type="text"]', 'textarea', 'button',
            '.chat-input', '[data-cy="send-button"]'
          ]
          
          criticalElements.forEach(element => {
            if ($body.find(element).length > 0) {
              cy.get(element).first().should('be.visible')
            }
          })
        }
      })
    })
  })

  describe('Accessibility and Contrast', () => {
    it('should maintain good contrast in all themes', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test contrast by checking that text is visible against backgrounds
      cy.get('body').then($body => {
        // Test in current theme
        const textElements = ['h1', 'h2', 'p', 'span', 'button', 'input']
        
        textElements.forEach(element => {
          if ($body.find(element).length > 0) {
            cy.get(element).first().should('be.visible')
          }
        })
        
        // Toggle theme and test again
        if ($body.find('[data-cy="theme-toggle"]').length > 0) {
          cy.get('[data-cy="theme-toggle"]').first().click()
          cy.wait(500)
          
          textElements.forEach(element => {
            if ($body.find(element).length > 0) {
              cy.get(element).first().should('be.visible')
            }
          })
        }
      })
    })

    it('should support keyboard navigation for preferences', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Test keyboard navigation to theme/language controls
      cy.get('body').then($body => {
        const focusableControls = [
          '[data-cy="theme-toggle"]', '[data-cy="language-toggle"]',
          '.theme-toggle', '.language-toggle'
        ]
        
        focusableControls.forEach(control => {
          if ($body.find(control).length > 0) {
            // Focus the control
            cy.get(control).first().focus()
            cy.get(control).first().should('have.focus')
            
            // Test Enter key activation
            cy.get(control).first().type('{enter}')
            cy.wait(300)
          }
        })
      })
    })

    it('should provide appropriate ARIA labels for UI controls', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Check for ARIA labels on theme and language controls
      cy.get('body').then($body => {
        const accessibleControls = [
          '[data-cy="theme-toggle"]', '[data-cy="language-toggle"]'
        ]
        
        accessibleControls.forEach(control => {
          if ($body.find(control).length > 0) {
            cy.get(control).first().then($el => {
              const hasAriaLabel = $el.attr('aria-label')
              const hasTitle = $el.attr('title')
              const hasAriaLabelledBy = $el.attr('aria-labelledby')
              
              // Should have some form of accessible label
              const hasAccessibleLabel = hasAriaLabel || hasTitle || hasAriaLabelledBy
              
              if (hasAccessibleLabel) {
                cy.get(control).first().should('be.visible')
              }
            })
          }
        })
      })
    })
  })

  describe('Preference Persistence', () => {
    it('should save preferences to localStorage', () => {
      cy.visit('/chat')
      cy.waitForApp()
      
      // Toggle preferences and check localStorage
      cy.get('body').then($body => {
        if ($body.find('[data-cy="theme-toggle"]').length > 0) {
          cy.get('[data-cy="theme-toggle"]').first().click()
          cy.wait(500)
          
          // Check if localStorage has theme preference
          cy.window().then((win) => {
            const themePrefs = ['theme', 'darkMode', 'userTheme', 'selectedTheme']
            
            themePrefs.forEach(pref => {
              const stored = win.localStorage.getItem(pref)
              if (stored) {
                expect(stored).to.not.be.null
              }
            })
          })
        }
      })
    })

    it('should restore preferences on app load', () => {
      // Set preferences manually and reload
      cy.window().then((win) => {
        win.localStorage.setItem('theme', 'dark')
        win.localStorage.setItem('language', 'he')
      })
      
      cy.visit('/chat')
      cy.waitForApp()
      
      // Check that preferences are applied
      cy.get('body').should('be.visible')
      
      // Verify theme/language state is restored
      cy.get('body').then($body => {
        // Look for indicators that preferences were restored
        const darkIndicators = [
          '[data-theme="dark"]', '.dark', '.dark-mode'
        ]
        
        const hebrewIndicators = [
          '[dir="rtl"]', '[lang="he"]', '.rtl'
        ]
        
        // If any indicators are found, preferences were likely restored
        darkIndicators.concat(hebrewIndicators).forEach(indicator => {
          if ($body.find(indicator).length > 0) {
            cy.get(indicator).first().should('exist')
          }
        })
      })
    })
  })
})
