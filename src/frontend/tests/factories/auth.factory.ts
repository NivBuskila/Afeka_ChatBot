import { faker } from '@faker-js/faker'

export interface MockUser {
  id: string
  email: string
  name?: string
  role: 'admin' | 'user'
  created_at: string
  updated_at: string
  last_sign_in_at?: string
  email_confirmed_at?: string
  phone?: string
  user_metadata?: Record<string, any>
  app_metadata?: Record<string, any>
}

export interface MockSession {
  access_token: string
  refresh_token: string
  expires_in: number
  token_type: string
  user: MockUser
}

export const createMockUser = (overrides: Partial<MockUser> = {}): MockUser => {
  const baseUser: MockUser = {
    id: faker.string.uuid(),
    email: faker.internet.email(),
    name: faker.person.fullName(),
    role: 'user',
    created_at: faker.date.past().toISOString(),
    updated_at: faker.date.recent().toISOString(),
    last_sign_in_at: faker.date.recent().toISOString(),
    email_confirmed_at: faker.date.past().toISOString(),
    phone: faker.helpers.maybe(() => faker.phone.number(), { probability: 0.3 }),
    user_metadata: {
      theme: faker.helpers.arrayElement(['light', 'dark']),
      language: faker.helpers.arrayElement(['en', 'he']),
    },
    app_metadata: {
      provider: 'email',
      providers: ['email']
    }
  }

  return {
    ...baseUser,
    ...overrides,
    updated_at: overrides.updated_at || baseUser.updated_at
  }
}

export const createMockSession = (overrides: Partial<MockSession> = {}): MockSession => {
  const baseSession: MockSession = {
    access_token: `mock-access-token-${faker.string.alphanumeric(32)}`,
    refresh_token: `mock-refresh-token-${faker.string.alphanumeric(32)}`,
    expires_in: 3600,
    token_type: 'bearer',
    user: createMockUser()
  }

  return {
    ...baseSession,
    ...overrides
  }
}

export const createMockAdminUser = (overrides: Partial<MockUser> = {}): MockUser => {
  return createMockUser({
    role: 'admin',
    email: 'admin@test.com',
    name: 'Test Administrator',
    app_metadata: {
      provider: 'email',
      providers: ['email'],
      role: 'admin'
    },
    ...overrides
  })
}

export const createMockRegularUser = (overrides: Partial<MockUser> = {}): MockUser => {
  return createMockUser({
    role: 'user',
    ...overrides
  })
}

// Factory for creating multiple users
export const createMockUsers = (count: number, overrides: Partial<MockUser> = {}): MockUser[] => {
  return Array.from({ length: count }, () => createMockUser(overrides))
}

// Factory for creating test credentials
export const createTestCredentials = (role: 'admin' | 'user' = 'user') => {
  const credentials = {
    admin: {
      email: 'admin@test.com',
      password: 'admin123',
      user: createMockAdminUser({ email: 'admin@test.com', id: 'admin-user-id' })
    },
    user: {
      email: 'user@test.com',
      password: 'user123',
      user: createMockRegularUser({ email: 'user@test.com', id: 'regular-user-id' })
    }
  }

  return credentials[role]
} 