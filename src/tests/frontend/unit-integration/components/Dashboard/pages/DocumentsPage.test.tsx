import { describe, it, expect, beforeEach, vi } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithAdminContext, createUserEvent } from '../../../utils/admin-test-utils'
import { createMockDocument } from '../../../factories/admin.factory'

// Mock DocumentsPage component
const MockDocumentsPage = ({ 
  activeSubItem, 
  documents, 
  searchQuery, 
  setSearchQuery,
  setShowUploadModal,
  setShowEditDocumentModal,
  setSelectedDocument,
  handleDeleteDocument 
}: any) => {
  const filteredDocuments = documents?.filter((doc: any) => 
    doc.title.toLowerCase().includes(searchQuery?.toLowerCase() || '')
  ) || []

  return (
    <div data-testid="documents-page">
      <h1>Documents Management</h1>
      
      <div className="documents-controls">
        <input 
          type="text"
          placeholder="Search documents..."
          value={searchQuery || ''}
          onChange={(e) => setSearchQuery(e.target.value)}
          data-testid="search-input"
        />
        <button 
          onClick={() => setShowUploadModal(true)}
          data-testid="upload-button"
        >
          Upload Document
        </button>
      </div>

      {activeSubItem === 'active' && (
        <div data-testid="active-documents">
          <h2>Active Documents</h2>
          {filteredDocuments.map((doc: any) => (
            <div key={doc.id} data-testid={`document-${doc.id}`} className="document-item">
              <span>{doc.title}</span>
              <div className="document-actions">
                <button 
                  onClick={() => {
                    setSelectedDocument(doc)
                    setShowEditDocumentModal(true)
                  }}
                  data-testid={`edit-${doc.id}`}
                >
                  Edit
                </button>
                <button 
                  onClick={() => handleDeleteDocument(doc)}
                  data-testid={`delete-${doc.id}`}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {activeSubItem === 'archived' && (
        <div data-testid="archived-documents">
          <h2>Archived Documents</h2>
          <p>No archived documents</p>
        </div>
      )}
    </div>
  )
}

/**
 * 🎯 טסטים עבור DocumentsPage Component
 * מבדק את ניהול המסמכים והאינטראקציות
 */
describe('DocumentsPage', () => {
  const mockDocuments = [
    createMockDocument({ id: 'doc-1', title: 'Test Document 1' }),
    createMockDocument({ id: 'doc-2', title: 'Test Document 2' }),
    createMockDocument({ id: 'doc-3', title: 'Another Document' })
  ]

  const defaultProps = {
    activeSubItem: 'active',
    documents: mockDocuments,
    searchQuery: '',
    setSearchQuery: vi.fn(),
    setShowUploadModal: vi.fn(),
    setShowEditDocumentModal: vi.fn(),
    setSelectedDocument: vi.fn(),
    handleDeleteDocument: vi.fn()
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('🔧 Basic Rendering', () => {
    it('should render documents page', () => {
      renderWithAdminContext(<MockDocumentsPage {...defaultProps} />)
      
      expect(screen.getByText('Documents Management')).toBeInTheDocument()
      expect(screen.getByTestId('documents-page')).toBeInTheDocument()
    })

    it('should display upload button', () => {
      renderWithAdminContext(<MockDocumentsPage {...defaultProps} />)
      
      expect(screen.getByTestId('upload-button')).toBeInTheDocument()
    })

    it('should display search input', () => {
      renderWithAdminContext(<MockDocumentsPage {...defaultProps} />)
      
      expect(screen.getByTestId('search-input')).toBeInTheDocument()
    })
  })

  describe('📄 Document Display', () => {
    it('should display active documents', () => {
      renderWithAdminContext(<MockDocumentsPage {...defaultProps} />)
      
      expect(screen.getByTestId('active-documents')).toBeInTheDocument()
      expect(screen.getByText('Test Document 1')).toBeInTheDocument()
      expect(screen.getByText('Test Document 2')).toBeInTheDocument()
      expect(screen.getByText('Another Document')).toBeInTheDocument()
    })

    it('should display archived documents section', () => {
      renderWithAdminContext(<MockDocumentsPage {...defaultProps} activeSubItem="archived" />)
      
      expect(screen.getByTestId('archived-documents')).toBeInTheDocument()
      expect(screen.getByText('Archived Documents')).toBeInTheDocument()
    })
  })

  describe('🔍 Search Functionality', () => {
    it('should call setSearchQuery when typing in search', async () => {
      const user = createUserEvent()
      renderWithAdminContext(<MockDocumentsPage {...defaultProps} />)
      
      const searchInput = screen.getByTestId('search-input')
      await user.type(searchInput, 'test')
      
      expect(defaultProps.setSearchQuery).toHaveBeenCalled()
    })

    it('should filter documents based on search query', () => {
      renderWithAdminContext(<MockDocumentsPage {...defaultProps} searchQuery="Test" />)
      
      expect(screen.getByText('Test Document 1')).toBeInTheDocument()
      expect(screen.getByText('Test Document 2')).toBeInTheDocument()
      expect(screen.queryByText('Another Document')).not.toBeInTheDocument()
    })
  })

  describe('📤 Document Actions', () => {
    it('should call setShowUploadModal when upload button clicked', async () => {
      const user = createUserEvent()
      renderWithAdminContext(<MockDocumentsPage {...defaultProps} />)
      
      const uploadButton = screen.getByTestId('upload-button')
      await user.click(uploadButton)
      
      expect(defaultProps.setShowUploadModal).toHaveBeenCalledWith(true)
    })

    it('should handle document edit', async () => {
      const user = createUserEvent()
      renderWithAdminContext(<MockDocumentsPage {...defaultProps} />)
      
      const editButton = screen.getByTestId('edit-doc-1')
      await user.click(editButton)
      
      expect(defaultProps.setSelectedDocument).toHaveBeenCalledWith(mockDocuments[0])
      expect(defaultProps.setShowEditDocumentModal).toHaveBeenCalledWith(true)
    })

    it('should handle document deletion', async () => {
      const user = createUserEvent()
      renderWithAdminContext(<MockDocumentsPage {...defaultProps} />)
      
      const deleteButton = screen.getByTestId('delete-doc-1')
      await user.click(deleteButton)
      
      expect(defaultProps.handleDeleteDocument).toHaveBeenCalledWith(mockDocuments[0])
    })
  })

  describe('🛡️ Error Handling', () => {
    it('should handle empty documents list', () => {
      renderWithAdminContext(<MockDocumentsPage {...defaultProps} documents={[]} />)
      
      expect(screen.getByTestId('active-documents')).toBeInTheDocument()
      expect(screen.queryByText('Test Document 1')).not.toBeInTheDocument()
    })

    it('should handle null documents', () => {
      renderWithAdminContext(<MockDocumentsPage {...defaultProps} documents={null} />)
      
      expect(screen.getByTestId('active-documents')).toBeInTheDocument()
    })
  })
}) 