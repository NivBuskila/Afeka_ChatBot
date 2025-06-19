# Frontend Test Suite Documentation

## 🚀 **Enhanced Test Infrastructure - Phase 1 Complete**

This document outlines the comprehensive testing strategy and implementation for the Afeka ChatBot frontend application.

## 📁 **Test Structure**

```
tests/
├── __mocks__/              # Module mocks
│   └── i18n.ts            # i18next mock
├── examples/              # Example tests demonstrating features
│   └── infrastructure.test.tsx
├── factories/             # Test data factories
│   ├── auth.factory.ts    # Authentication-related test data
│   ├── chat.factory.ts    # Chat/messaging test data
│   ├── document.factory.ts # Document management test data
│   └── analytics.factory.ts # Analytics/metrics test data
├── mocks/                 # MSW API handlers
│   ├── handlers.ts        # Main handler exports
│   ├── auth.handlers.ts   # Authentication endpoints
│   ├── chat.handlers.ts   # Chat/messaging endpoints
│   ├── document.handlers.ts # Document management endpoints
│   ├── analytics.handlers.ts # Analytics endpoints
│   └── user.handlers.ts   # User management endpoints
├── utils/                 # Test utilities
│   └── test-utils.tsx     # Custom render functions and helpers
├── components/            # Component tests (to be created)
├── services/              # Service tests (to be created)
├── integration/           # Integration tests (to be created)
├── setup.ts              # Test environment setup
└── README.md             # This file
```

## 🛠 **Testing Stack**

- **Test Runner**: Vitest
- **Testing Library**: @testing-library/react + @testing-library/user-event
- **API Mocking**: MSW (Mock Service Worker)
- **Test Data**: @faker-js/faker
- **Coverage**: v8 provider
- **Environment**: jsdom

## 🎯 **Test Infrastructure Features**

### ✅ **Phase 1: Enhanced Test Infrastructure** (COMPLETE)

#### 1.1 **MSW Integration**
- Complete API mocking setup with realistic handlers
- Authentication flow mocking
- CRUD operations for all entities
- Error scenario testing
- Stateful mocks with in-memory data

#### 1.2 **Test Data Factories**
- **Authentication**: Users, sessions, credentials
- **Chat**: Sessions, messages, conversations
- **Documents**: Files, chunks, processing states
- **Analytics**: Usage metrics, performance data

#### 1.3 **Enhanced Test Utilities**
- Custom render functions with providers
- Authentication context helpers
- Theme and language context support
- Router integration
- Assertion helpers

#### 1.4 **Mock Services**
- Supabase client mocking
- i18next internationalization mocking
- Context providers mocking

## 🚀 **Quick Start**

### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test path/to/test.file

# Run tests matching pattern
npm test -- --grep "pattern"
```

### Writing Tests

#### Basic Component Test
```typescript
import { render, screen } from '@/tests/utils/test-utils'
import { MyComponent } from '../MyComponent'

describe('MyComponent', () => {
  it('should render correctly', () => {
    render(<MyComponent />)
    expect(screen.getByText('Hello World')).toBeInTheDocument()
  })
})
```

#### Authenticated Component Test
```typescript
import { renderWithAuth } from '@/tests/utils/test-utils'
import { AdminComponent } from '../AdminComponent'

describe('AdminComponent', () => {
  it('should render for admin users', () => {
    renderWithAuth(<AdminComponent />, { isAdmin: true })
    expect(screen.getByText('Admin Panel')).toBeInTheDocument()
  })
})
```

#### API Integration Test
```typescript
import { server } from '@/tests/setup'
import { http, HttpResponse } from 'msw'
import { createMockUser } from '@/tests/factories/auth.factory'

describe('User API Integration', () => {
  it('should fetch user data', async () => {
    const mockUser = createMockUser({ name: 'John Doe' })
    
    server.use(
      http.get('/api/user/profile', () => {
        return HttpResponse.json({ data: mockUser })
      })
    )

    // Test implementation
  })
})
```

## 📋 **Test Coverage Targets**

- **Global Coverage**: 70% minimum
- **Critical Components**: 90%+ 
- **Business Logic**: 95%+
- **UI Components**: 80%+

Current thresholds:
- Branches: 70%
- Functions: 70%
- Lines: 70%
- Statements: 70%

## 🧪 **Testing Patterns**

### 1. **Component Testing**
- Render testing
- User interaction testing
- Props validation
- State management testing
- Event handling

### 2. **Service Testing**
- API call testing
- Error handling
- Cache behavior
- Authentication flows

### 3. **Integration Testing**
- User workflows
- Cross-component interactions
- API integration
- Authentication flows

### 4. **Accessibility Testing**
- Screen reader compatibility
- Keyboard navigation
- ARIA attributes
- Color contrast

## 🔧 **Available Test Utilities**

### Render Functions
- `render()` - Enhanced render with all providers
- `renderWithAuth()` - Render with authentication context
- `renderWithRoute()` - Render with specific route
- `renderWithTheme()` - Render with specific theme
- `renderWithLanguage()` - Render with specific language

### Mock Factories
- `createMockUser()` - Generate user data
- `createMockChatSession()` - Generate chat session
- `createMockMessage()` - Generate chat message
- `createMockDocument()` - Generate document data
- `createMockAnalyticsData()` - Generate analytics metrics

### Assertion Helpers
- `expectElementToBeVisible()` - Visibility assertions
- `expectElementToHaveText()` - Text content assertions
- `waitForLoadingToFinish()` - Loading state helpers

## 🎯 **Next Phases (Roadmap)**

### **Phase 2: Component Testing Suite**
- [ ] Chat component tests
- [ ] Dashboard component tests  
- [ ] Form component tests
- [ ] UI component tests

### **Phase 3: Service Testing Suite**
- [ ] API service tests
- [ ] Authentication service tests
- [ ] Cache service tests
- [ ] Utility service tests

### **Phase 4: Integration Testing**
- [ ] User workflow tests
- [ ] Cross-component integration
- [ ] API integration tests
- [ ] E2E scenario tests

### **Phase 5: Advanced Testing**
- [ ] Performance testing
- [ ] Accessibility testing
- [ ] Visual regression testing
- [ ] Security testing

## 📊 **Test Metrics**

### Current Status
- ✅ Test Infrastructure: Complete
- ✅ MSW Setup: Complete
- ✅ Mock Factories: Complete
- ✅ Test Utilities: Complete
- ⏳ Component Tests: 0/50+ components
- ⏳ Service Tests: 0/10+ services
- ⏳ Integration Tests: 0/20+ workflows

### Coverage Goals
- Phase 1: Infrastructure (100% ✅)
- Phase 2: Components (Target: 80%)
- Phase 3: Services (Target: 90%)
- Phase 4: Integration (Target: 70%)
- Phase 5: Advanced (Target: 60%)

## 🤝 **Contributing to Tests**

### Guidelines
1. **Test Naming**: Use descriptive test names
2. **Test Structure**: Arrange-Act-Assert pattern
3. **Mock Data**: Use factories for consistent data
4. **Async Testing**: Proper async/await usage
5. **Coverage**: Aim for meaningful coverage, not just numbers

### Best Practices
- Write tests before fixing bugs
- Test edge cases and error scenarios
- Keep tests focused and isolated
- Use meaningful assertions
- Document complex test scenarios

## 🔍 **Debugging Tests**

### Common Issues
- **MSW not intercepting**: Check handler patterns
- **Component not rendering**: Verify provider setup
- **Async test failures**: Use proper waiting strategies
- **Mock data issues**: Check factory configurations

### Debug Commands
```bash
# Run with debug output
npm test -- --reporter=verbose

# Run single test with debugging
npm test -- --run --reporter=verbose path/to/test

# Check coverage details
npm run test:coverage -- --reporter=detailed
```

---

## 📞 **Support**

For questions about the test infrastructure:
1. Check existing example tests in `tests/examples/`
2. Review factory implementations in `tests/factories/`
3. Examine MSW handlers in `tests/mocks/`
4. Consult this documentation

**The enhanced test infrastructure is ready for Phase 2 implementation!** 🚀 