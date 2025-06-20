import { http, HttpResponse } from 'msw'
import { createMockChatSession, createMockMessage, createMockChatResponse } from '../factories/chat.factory'

let mockChatSessions: any[] = []
let mockMessages: any[] = []
let messageIdCounter = 1
let sessionIdCounter = 1

export const chatHandlers = [
  // Get chat sessions
  http.get('*/api/chat-sessions', ({ request }) => {
    const url = new URL(request.url)
    const userId = url.searchParams.get('user_id')
    
    return HttpResponse.json({
      data: mockChatSessions.filter(session => 
        !userId || session.user_id === userId
      ),
      count: mockChatSessions.length
    })
  }),
  
  // Create chat session
  http.post('*/api/chat-sessions', async ({ request }) => {
    const { title, user_id } = await request.json()
    
    const newSession = createMockChatSession({
      id: `session-${sessionIdCounter++}`,
      title: title || 'New Chat',
      user_id: user_id || 'test-user-id'
    })
    
    mockChatSessions.push(newSession)
    
    return HttpResponse.json({ data: newSession }, { status: 201 })
  }),
  
  // Send message and get AI response
  http.post('*/api/chat', async ({ request }) => {
    const { message, session_id, user_id } = await request.json()
    
    if (!message || !session_id) {
      return HttpResponse.json(
        { error: 'Message and session_id are required' },
        { status: 400 }
      )
    }
    
    // Create user message
    const userMessage = createMockMessage({
      id: `msg-${messageIdCounter++}`,
      session_id,
      user_id: user_id || 'test-user-id',
      content: message,
      role: 'user'
    })
    
    mockMessages.push(userMessage)
    
    // Generate AI response based on message content
    let aiResponse = "I'm a mock AI assistant. I received your message: " + message
    
    if (message.toLowerCase().includes('error')) {
      return HttpResponse.json(
        { error: 'Failed to generate response' },
        { status: 500 }
      )
    }
    
    if (message.toLowerCase().includes('hello')) {
      aiResponse = "Hello! How can I help you today?"
    } else if (message.toLowerCase().includes('help')) {
      aiResponse = "I'm here to help! What would you like to know?"
    }
    
    // Create AI message
    const aiMessage = createMockMessage({
      id: `msg-${messageIdCounter++}`,
      session_id,
      user_id: user_id || 'test-user-id',
      content: aiResponse,
      role: 'assistant'
    })
    
    mockMessages.push(aiMessage)
    
    return HttpResponse.json({
      data: {
        user_message: userMessage,
        ai_message: aiMessage,
        session_id
      }
    })
  }),
]

// Helper function to reset mock data
export const resetChatMockData = () => {
  mockChatSessions = []
  mockMessages = []
  messageIdCounter = 1
  sessionIdCounter = 1
}
