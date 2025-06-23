import { faker } from '@faker-js/faker'

export interface MockDashboardAnalytics {
  totalDocuments: number
  totalUsers: number
  totalAdmins: number
  recentDocuments: MockDocument[]
  recentUsers: MockUser[]
  recentAdmins: MockUser[]
}

export interface MockDocument {
  id: string
  name: string
  type: string
  size: number
  url: string
  created_at: string
  updated_at: string
}

export interface MockUser {
  id: string
  email: string
  name?: string
  created_at: string
  status?: string
  department?: string
}

export interface MockAdminState {
  activeItem: string
  activeSubItem: string | null
  showUploadModal: boolean
  showDeleteModal: boolean
  showDeleteUserModal: boolean
  showEditDocumentModal: boolean
  selectedDocument: MockDocument | null
  selectedUser: MockUser | null
  isInitialLoading: boolean
  isRefreshing: boolean
  successMessage: string
  errorMessage: string
  language: 'he' | 'en'
  theme: 'light' | 'dark'
}

export const createMockDocument = (overrides: Partial<MockDocument> = {}): MockDocument => {
  const baseDocument: MockDocument = {
    id: faker.string.uuid(),
    name: faker.system.fileName({ extensionCount: 1 }),
    type: faker.helpers.arrayElement(['application/pdf', 'text/plain', 'image/jpeg']),
    size: faker.number.int({ min: 1024, max: 10485760 }), // 1KB to 10MB
    url: faker.internet.url(),
    created_at: faker.date.recent().toISOString(),
    updated_at: faker.date.recent().toISOString()
  }

  return {
    ...baseDocument,
    ...overrides
  }
}

export const createMockUser = (overrides: Partial<MockUser> = {}): MockUser => {
  const baseUser: MockUser = {
    id: faker.string.uuid(),
    email: faker.internet.email(),
    name: faker.person.fullName(),
    created_at: faker.date.recent().toISOString(),
    status: faker.helpers.arrayElement(['active', 'inactive'])
  }

  return {
    ...baseUser,
    ...overrides
  }
}

export const createMockAdmin = (overrides: Partial<MockUser> = {}): MockUser => {
  return createMockUser({
    department: faker.helpers.arrayElement(['IT', 'Academic', 'Administration']),
    ...overrides
  })
}

export const createMockDashboardAnalytics = (overrides: Partial<MockDashboardAnalytics> = {}): MockDashboardAnalytics => {
  const baseAnalytics: MockDashboardAnalytics = {
    totalDocuments: faker.number.int({ min: 10, max: 100 }),
    totalUsers: faker.number.int({ min: 50, max: 500 }),
    totalAdmins: faker.number.int({ min: 2, max: 10 }),
    recentDocuments: Array.from({ length: 5 }, () => createMockDocument()),
    recentUsers: Array.from({ length: 20 }, () => createMockUser()),
    recentAdmins: Array.from({ length: 3 }, () => createMockAdmin())
  }

  return {
    ...baseAnalytics,
    ...overrides
  }
}

export const createMockAdminState = (overrides: Partial<MockAdminState> = {}): MockAdminState => {
  const baseState: MockAdminState = {
    activeItem: 'chatbot',
    activeSubItem: null,
    showUploadModal: false,
    showDeleteModal: false,
    showDeleteUserModal: false,
    showEditDocumentModal: false,
    selectedDocument: null,
    selectedUser: null,
    isInitialLoading: false,
    isRefreshing: false,
    successMessage: '',
    errorMessage: '',
    language: 'en',
    theme: 'light'
  }

  return {
    ...baseState,
    ...overrides
  }
}

// Helper function to create API mock responses
export const mockAdminAPI = () => {
  const analytics = createMockDashboardAnalytics()
  const documents = Array.from({ length: 10 }, () => createMockDocument())
  
  return {
    analytics,
    documents,
    uploadDocument: createMockDocument(),
    deleteResponse: { success: true, message: 'Document deleted successfully' },
    updateDocument: createMockDocument({ updated_at: new Date().toISOString() })
  }
} 