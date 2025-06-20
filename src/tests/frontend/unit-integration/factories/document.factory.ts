import { faker } from '@faker-js/faker'

export interface MockDocument {
  id: string
  title: string
  filename: string
  size: number
  type: string
  user_id: string
  created_at: string
  updated_at: string
  processing_status: 'pending' | 'processing' | 'completed' | 'failed'
  processed_at?: string
  chunks_count?: number
  url?: string
  metadata?: Record<string, any>
}

export interface MockDocumentChunk {
  id: string
  document_id: string
  content: string
  chunk_index: number
  token_count: number
  embedding?: number[]
  metadata?: Record<string, any>
}

export const createMockDocument = (overrides: Partial<MockDocument> = {}): MockDocument => {
  const fileTypes = [
    { type: 'application/pdf', ext: 'pdf' },
    { type: 'text/plain', ext: 'txt' },
    { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', ext: 'docx' },
    { type: 'text/markdown', ext: 'md' }
  ]
  
  const selectedType = faker.helpers.arrayElement(fileTypes)
  const baseFilename = faker.system.fileName({ extensionCount: 0 })
  const filename = `${baseFilename}.${selectedType.ext}`
  
  const status = faker.helpers.arrayElement(['pending', 'processing', 'completed', 'failed'])
  
  const baseDocument: MockDocument = {
    id: faker.string.uuid(),
    title: faker.helpers.arrayElement([
      'User Manual',
      'Technical Documentation',
      'API Reference',
      'Getting Started Guide',
      'FAQ Document',
      faker.lorem.words(3)
    ]),
    filename,
    size: faker.number.int({ min: 1024, max: 10485760 }), // 1KB to 10MB
    type: selectedType.type,
    user_id: faker.string.uuid(),
    created_at: faker.date.past().toISOString(),
    updated_at: faker.date.recent().toISOString(),
    processing_status: status,
    processed_at: status === 'completed' ? faker.date.recent().toISOString() : undefined,
    chunks_count: status === 'completed' ? faker.number.int({ min: 5, max: 100 }) : undefined,
    url: faker.internet.url(),
    metadata: {
      original_name: filename,
      content_type: selectedType.type,
      language: faker.helpers.arrayElement(['en', 'he']),
      pages: selectedType.ext === 'pdf' ? faker.number.int({ min: 1, max: 50 }) : undefined
    }
  }

  return {
    ...baseDocument,
    ...overrides
  }
}

export const createMockDocumentChunk = (overrides: Partial<MockDocumentChunk> = {}): MockDocumentChunk => {
  const content = faker.lorem.paragraphs(faker.number.int({ min: 1, max: 3 }))
  
  const baseChunk: MockDocumentChunk = {
    id: faker.string.uuid(),
    document_id: faker.string.uuid(),
    content,
    chunk_index: faker.number.int({ min: 0, max: 99 }),
    token_count: faker.number.int({ min: 50, max: 400 }),
    embedding: Array.from({ length: 1536 }, () => faker.number.float({ min: -1, max: 1, fractionDigits: 8 })),
    metadata: {
      page_number: faker.number.int({ min: 1, max: 50 }),
      section: faker.lorem.words(2),
      confidence: faker.number.float({ min: 0.6, max: 1.0, fractionDigits: 2 })
    }
  }

  return {
    ...baseChunk,
    ...overrides
  }
}

// Factory for creating multiple documents
export const createMockDocuments = (count: number, userId?: string): MockDocument[] => {
  return Array.from({ length: count }, () => 
    createMockDocument(userId ? { user_id: userId } : {})
  )
}

// Factory for creating documents with specific status
export const createMockProcessedDocument = (overrides: Partial<MockDocument> = {}): MockDocument => {
  return createMockDocument({
    processing_status: 'completed',
    processed_at: faker.date.recent().toISOString(),
    chunks_count: faker.number.int({ min: 10, max: 50 }),
    ...overrides
  })
}

export const createMockPendingDocument = (overrides: Partial<MockDocument> = {}): MockDocument => {
  return createMockDocument({
    processing_status: 'pending',
    processed_at: undefined,
    chunks_count: undefined,
    ...overrides
  })
}

export const createMockFailedDocument = (overrides: Partial<MockDocument> = {}): MockDocument => {
  return createMockDocument({
    processing_status: 'failed',
    processed_at: faker.date.recent().toISOString(),
    chunks_count: 0,
    metadata: {
      error: faker.helpers.arrayElement([
        'File format not supported',
        'File too large',
        'Processing timeout',
        'Corrupted file'
      ]),
      retry_count: faker.number.int({ min: 1, max: 3 })
    },
    ...overrides
  })
}

// Factory for creating document chunks for a specific document
export const createMockDocumentChunks = (documentId: string, count: number): MockDocumentChunk[] => {
  return Array.from({ length: count }, (_, index) => 
    createMockDocumentChunk({
      document_id: documentId,
      chunk_index: index
    })
  )
}

// Factory for creating a file object (for upload testing)
export const createMockFile = (overrides: Partial<File> = {}): File => {
  const defaultFile = {
    name: 'test-document.pdf',
    size: 1024000, // 1MB
    type: 'application/pdf',
    lastModified: Date.now()
  }

  const fileOptions = { ...defaultFile, ...overrides }
  const content = faker.lorem.paragraphs(10)
  
  return new File([content], fileOptions.name, {
    type: fileOptions.type,
    lastModified: fileOptions.lastModified
  })
}

// Factory for creating multiple file objects
export const createMockFiles = (count: number): File[] => {
  const fileTypes = [
    { name: 'document.pdf', type: 'application/pdf' },
    { name: 'readme.txt', type: 'text/plain' },
    { name: 'manual.docx', type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' },
    { name: 'guide.md', type: 'text/markdown' }
  ]

  return Array.from({ length: count }, (_, index) => {
    const fileType = faker.helpers.arrayElement(fileTypes)
    return createMockFile({
      name: `${faker.system.fileName({ extensionCount: 0 })}-${index + 1}.${fileType.name.split('.').pop()}`,
      type: fileType.type,
      size: faker.number.int({ min: 1024, max: 5242880 }) // 1KB to 5MB
    })
  })
} 