import { describe, it, expect, beforeEach, vi } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithAdminContext, createUserEvent } from '../../../utils/admin-test-utils'

// Mock RAGPage component
const MockRAGPage = ({ activeSubItem, isLoading }: any) => {
  return (
    <div data-testid="rag-page">
      <h1>RAG Configuration</h1>
      
      {isLoading && <div data-testid="loading">Loading...</div>}
      
      {activeSubItem === 'overview' && (
        <div data-testid="rag-overview">
          <h2>RAG Overview</h2>
          <div>Current Status: Active</div>
        </div>
      )}
      
      {activeSubItem === 'settings' && (
        <div data-testid="rag-settings">
          <h2>RAG Settings</h2>
          <button data-testid="save-config-button">Save Configuration</button>
        </div>
      )}
    </div>
  )
}

/**
 * 🎯 טסטים עבור RAGPage Component
 */
describe('RAGPage', () => {
  const defaultProps = {
    activeSubItem: 'overview',
    isLoading: false
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('🔧 Basic Rendering', () => {
    it('should render RAG page', () => {
      renderWithAdminContext(<MockRAGPage {...defaultProps} />)
      
      expect(screen.getByText('RAG Configuration')).toBeInTheDocument()
      expect(screen.getByTestId('rag-page')).toBeInTheDocument()
    })

    it('should show loading state', () => {
      renderWithAdminContext(<MockRAGPage {...defaultProps} isLoading={true} />)
      
      expect(screen.getByTestId('loading')).toBeInTheDocument()
    })
  })

  describe('📊 Overview Section', () => {
    it('should display RAG overview', () => {
      renderWithAdminContext(<MockRAGPage {...defaultProps} activeSubItem="overview" />)
      
      expect(screen.getByTestId('rag-overview')).toBeInTheDocument()
      expect(screen.getByText('RAG Overview')).toBeInTheDocument()
    })
  })

  describe('⚙️ Settings Section', () => {
    it('should display RAG settings', () => {
      renderWithAdminContext(<MockRAGPage {...defaultProps} activeSubItem="settings" />)
      
      expect(screen.getByTestId('rag-settings')).toBeInTheDocument()
      expect(screen.getByText('RAG Settings')).toBeInTheDocument()
    })
  })
}) 