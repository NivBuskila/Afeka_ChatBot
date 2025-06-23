import { http, HttpResponse } from 'msw'
import { authHandlers } from './auth.handlers'
import { chatHandlers } from './chat.handlers'
import { documentHandlers } from './document.handlers'
import { analyticsHandlers } from './analytics.handlers'
import { userHandlers } from './user.handlers'
import { adminHandlers } from './admin.handlers'

// Combine all handlers
export const handlers = [
  ...authHandlers,
  ...chatHandlers,
  ...documentHandlers,
  ...analyticsHandlers,
  ...userHandlers,
  ...adminHandlers,
  
  // Generic error handler for unhandled requests
  http.all('*', ({ request }) => {
    console.warn(`Unhandled ${request.method} request to ${request.url}`)
    return HttpResponse.json(
      { message: 'API endpoint not mocked' },
      { status: 404 }
    )
  }),
] 