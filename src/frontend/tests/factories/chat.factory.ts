import { faker } from '@faker-js/faker'

export interface MockChatSession {
  id: string
  title: string
  user_id: string
  created_at: string
  updated_at: string
  message_count?: number
  last_message_at?: string
}

export interface MockMessage {
  id: string
  session_id: string
  user_id: string
  content: string
  role: 'user' | 'assistant'
  created_at: string
  updated_at: string
  metadata?: Record<string, any>
  token_count?: number
}

export interface MockChatResponse {
  message: string
  session_id: string
  context?: string[]
  confidence?: number
  sources?: string[]
}

export const createMockChatSession = (overrides: Partial<MockChatSession> = {}): MockChatSession => {
  const baseSession: MockChatSession = {
    id: faker.string.uuid(),
    title: faker.helpers.arrayElement([
      'Help with documentation',
      'Technical support question',
      'How to use the system',
      'General inquiry',
      faker.lorem.words(3)
    ]),
    user_id: faker.string.uuid(),
    created_at: faker.date.past().toISOString(),
    updated_at: faker.date.recent().toISOString(),
    message_count: faker.number.int({ min: 1, max: 50 }),
    last_message_at: faker.date.recent().toISOString()
  }

  return {
    ...baseSession,
    ...overrides
  }
}

export const createMockMessage = (overrides: Partial<MockMessage> = {}): MockMessage => {
  const role = overrides.role || faker.helpers.arrayElement(['user', 'assistant'])
  
  let content: string
  if (role === 'user') {
    content = faker.helpers.arrayElement([
      'Hello, I need help with something',
      'How do I upload a document?',
      'Can you help me understand this feature?',
      'What are the system requirements?',
      'I\'m having trouble with login',
      faker.lorem.sentence()
    ])
  } else {
    content = faker.helpers.arrayElement([
      'Hello! I\'m here to help. What can I assist you with today?',
      'To upload a document, you can use the upload button in the Documents section.',
      'I\'d be happy to explain that feature. Let me provide you with the details.',
      'Here are the system requirements you requested...',
      'I can help you with login issues. Let me guide you through the steps.',
      `I understand you're asking about ${faker.lorem.words(2)}. Here's what I can tell you: ${faker.lorem.paragraph()}`
    ])
  }

  const baseMessage: MockMessage = {
    id: faker.string.uuid(),
    session_id: faker.string.uuid(),
    user_id: faker.string.uuid(),
    content,
    role,
    created_at: faker.date.recent().toISOString(),
    updated_at: faker.date.recent().toISOString(),
    token_count: faker.number.int({ min: 10, max: 500 }),
    metadata: role === 'assistant' ? {
      model: 'gpt-3.5-turbo',
      response_time: faker.number.int({ min: 500, max: 3000 }),
      confidence: faker.number.float({ min: 0.7, max: 1.0, fractionDigits: 2 })
    } : undefined
  }

  return {
    ...baseMessage,
    ...overrides
  }
}

export const createMockChatResponse = (overrides: Partial<MockChatResponse> = {}): MockChatResponse => {
  const baseResponse: MockChatResponse = {
    message: faker.lorem.paragraph(),
    session_id: faker.string.uuid(),
    context: faker.helpers.maybe(() => 
      Array.from({ length: faker.number.int({ min: 1, max: 3 }) }, () => faker.lorem.sentence()),
      { probability: 0.7 }
    ),
    confidence: faker.number.float({ min: 0.6, max: 1.0, fractionDigits: 2 }),
    sources: faker.helpers.maybe(() => 
      Array.from({ length: faker.number.int({ min: 1, max: 3 }) }, () => 
        `Document ${faker.number.int({ min: 1, max: 100 })}: ${faker.lorem.words(3)}`
      ),
      { probability: 0.5 }
    )
  }

  return {
    ...baseResponse,
    ...overrides
  }
}

// Factory for creating a conversation (multiple messages)
export const createMockConversation = (sessionId: string, messageCount: number = 5): MockMessage[] => {
  const messages: MockMessage[] = []
  const userId = faker.string.uuid()
  
  for (let i = 0; i < messageCount; i++) {
    const isUserMessage = i % 2 === 0 // Alternate between user and assistant
    const createdAt = new Date(Date.now() - (messageCount - i) * 60000) // Space messages 1 minute apart
    
    messages.push(createMockMessage({
      session_id: sessionId,
      user_id: userId,
      role: isUserMessage ? 'user' : 'assistant',
      created_at: createdAt.toISOString(),
      updated_at: createdAt.toISOString()
    }))
  }
  
  return messages
}

// Factory for creating multiple chat sessions
export const createMockChatSessions = (count: number, userId?: string): MockChatSession[] => {
  return Array.from({ length: count }, () => 
    createMockChatSession(userId ? { user_id: userId } : {})
  )
}

// Factory for specific message types
export const createMockUserMessage = (content: string, overrides: Partial<MockMessage> = {}): MockMessage => {
  return createMockMessage({
    role: 'user',
    content,
    ...overrides
  })
}

export const createMockAssistantMessage = (content: string, overrides: Partial<MockMessage> = {}): MockMessage => {
  return createMockMessage({
    role: 'assistant',
    content,
    metadata: {
      model: 'gpt-3.5-turbo',
      response_time: faker.number.int({ min: 500, max: 3000 }),
      confidence: faker.number.float({ min: 0.7, max: 1.0, fractionDigits: 2 })
    },
    ...overrides
  })
}

// Factory for creating message pairs (user question + assistant response)
export const createMockMessagePair = (sessionId: string, userContent?: string, assistantContent?: string): MockMessage[] => {
  const timestamp = faker.date.recent()
  const userMessage = createMockUserMessage(
    userContent || 'Hello, I need help with something',
    {
      session_id: sessionId,
      created_at: timestamp.toISOString(),
      updated_at: timestamp.toISOString()
    }
  )
  
  const responseTimestamp = new Date(timestamp.getTime() + 5000) // 5 seconds later
  const assistantMessage = createMockAssistantMessage(
    assistantContent || 'Hello! I\'m here to help. What can I assist you with?',
    {
      session_id: sessionId,
      user_id: userMessage.user_id,
      created_at: responseTimestamp.toISOString(),
      updated_at: responseTimestamp.toISOString()
    }
  )
  
  return [userMessage, assistantMessage]
} 