import { http, HttpResponse } from 'msw'
import { createMockDocument } from '../factories/document.factory'

let mockDocuments: any[] = []
let documentIdCounter = 1

export const documentHandlers = [
  // Get documents
  http.get('*/api/documents', ({ request }) => {
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const limit = parseInt(url.searchParams.get('limit') || '10')
    
    // Pagination
    const startIndex = (page - 1) * limit
    const paginatedDocs = mockDocuments.slice(startIndex, startIndex + limit)
    
    return HttpResponse.json({
      data: paginatedDocs,
      count: mockDocuments.length,
      page,
      limit
    })
  }),
  
  // Upload document
  http.post('*/api/documents/upload', async ({ request }) => {
    const formData = await request.formData()
    const file = formData.get('file') as File
    const title = formData.get('title') as string
    
    if (!file) {
      return HttpResponse.json(
        { error: 'File is required' },
        { status: 400 }
      )
    }
    
    // Simulate upload delay
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const newDocument = createMockDocument({
      id: `doc-${documentIdCounter++}`,
      title: title || file.name,
      filename: file.name,
      size: file.size,
      type: file.type
    })
    
    mockDocuments.push(newDocument)
    
    return HttpResponse.json({ data: newDocument }, { status: 201 })
  }),
  
  // Delete document
  http.delete('*/api/documents/:documentId', ({ params }) => {
    const { documentId } = params
    
    const docIndex = mockDocuments.findIndex(d => d.id === documentId)
    if (docIndex === -1) {
      return HttpResponse.json(
        { error: 'Document not found' },
        { status: 404 }
      )
    }
    
    mockDocuments.splice(docIndex, 1)
    
    return HttpResponse.json({}, { status: 204 })
  }),
  
  // Process document
  http.post('*/api/documents/:documentId/process', async ({ params }) => {
    const { documentId } = params
    
    const doc = mockDocuments.find(d => d.id === documentId)
    if (!doc) {
      return HttpResponse.json(
        { error: 'Document not found' },
        { status: 404 }
      )
    }
    
    // Simulate processing
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    doc.processing_status = 'completed'
    doc.processed_at = new Date().toISOString()
    doc.chunks_count = Math.floor(Math.random() * 50) + 10
    
    return HttpResponse.json({ data: doc })
  }),
  
  // Get document chunks
  http.get('*/api/documents/:documentId/chunks', ({ params, request }) => {
    const { documentId } = params
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const limit = parseInt(url.searchParams.get('limit') || '20')
    
    const doc = mockDocuments.find(d => d.id === documentId)
    if (!doc) {
      return HttpResponse.json(
        { error: 'Document not found' },
        { status: 404 }
      )
    }
    
    // Generate mock chunks
    const chunksCount = doc.chunks_count || 0
    const chunks = Array.from({ length: chunksCount }, (_, i) => ({
      id: `chunk-${documentId}-${i + 1}`,
      document_id: documentId,
      content: `This is chunk ${i + 1} of document ${doc.title}. Lorem ipsum dolor sit amet, consectetur adipiscing elit.`,
      chunk_index: i,
      token_count: Math.floor(Math.random() * 200) + 50
    }))
    
    // Pagination
    const startIndex = (page - 1) * limit
    const paginatedChunks = chunks.slice(startIndex, startIndex + limit)
    
    return HttpResponse.json({
      data: paginatedChunks,
      count: chunks.length,
      page,
      limit
    })
  }),
]

// Helper function to reset mock data
export const resetDocumentMockData = () => {
  mockDocuments = []
  documentIdCounter = 1
}
