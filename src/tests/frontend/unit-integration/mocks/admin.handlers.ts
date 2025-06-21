import { http, HttpResponse } from 'msw'
import { createMockDashboardAnalytics, createMockDocument } from '../factories/admin.factory'

export const adminHandlers = [
  // Get dashboard analytics
  http.get('/api/analytics/dashboard', () => {
    const analytics = createMockDashboardAnalytics()
    return HttpResponse.json(analytics)
  }),

  // Get all documents
  http.get('/api/documents', () => {
    const documents = Array.from({ length: 10 }, () => createMockDocument())
    return HttpResponse.json(documents)
  }),

  // Upload document
  http.post('/api/documents/upload', async ({ request }) => {
    const formData = await request.formData()
    const file = formData.get('file') as File
    
    if (!file) {
      return HttpResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      )
    }

    const newDocument = createMockDocument({
      name: file.name,
      type: file.type,
      size: file.size
    })

    return HttpResponse.json(newDocument, { status: 201 })
  }),

  // Update document
  http.put('/api/documents/:id', async ({ params, request }) => {
    const documentId = params.id
    const formData = await request.formData()
    const file = formData.get('file') as File

    const updatedDocument = createMockDocument({
      id: String(documentId),
      name: file?.name || 'updated-document.pdf',
      type: file?.type || 'application/pdf',
      size: file?.size || 12345,
      updated_at: new Date().toISOString()
    })

    return HttpResponse.json(updatedDocument)
  }),

  // Delete document
  http.delete('/api/documents/:id', ({ params }) => {
    const documentId = params.id
    return HttpResponse.json({ 
      success: true, 
      message: `Document ${documentId} deleted successfully` 
    })
  }),

  // Delete user
  http.delete('/api/users/:id', ({ params }) => {
    const userId = params.id
    return HttpResponse.json({ 
      success: true, 
      message: `User ${userId} deleted successfully` 
    })
  }),

  // Get user session (for authentication)
  http.get('/api/auth/session', () => {
    return HttpResponse.json({
      data: {
        session: {
          user: {
            id: 'admin-user-id',
            email: 'admin@test.com',
            user_metadata: {
              is_admin: true,
              role: 'admin'
            }
          }
        }
      },
      error: null
    })
  }),
  
  // Error scenarios for testing
  http.post('/api/documents/upload-error', () => {
    return HttpResponse.json(
      { error: 'Upload failed - server error' },
      { status: 500 }
    )
  }),

  http.delete('/api/documents/delete-error/:id', () => {
    return HttpResponse.json(
      { error: 'Delete failed - document not found' },
      { status: 404 }
    )
  })
] 