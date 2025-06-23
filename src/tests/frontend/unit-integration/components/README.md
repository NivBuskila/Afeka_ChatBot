# 🧪 Phase 2: Component Testing Suite

## Overview

This directory contains comprehensive component tests for the APEX frontend application. The testing suite covers all major UI components, from basic atoms to complex molecules and organisms.

## 📁 Directory Structure

```
tests/components/
├── ui/                    # Basic UI components (atoms)
│   ├── Button.test.tsx
│   ├── Input.test.tsx
│   ├── ThemeButton.test.tsx
│   ├── ThemeInput.test.tsx
│   └── ThemeCard.test.tsx
├── Chat/                  # Chat-related components (molecules)
│   ├── ChatInput.test.tsx
│   ├── ChatWindow.test.tsx
│   ├── MessageItem.test.tsx
│   ├── MessageList.test.tsx
│   └── ChatHistory.test.tsx
├── Dashboard/             # Admin dashboard components (organisms)
│   ├── AdminDashboard.test.tsx
│   ├── DocumentTable.test.tsx
│   ├── UserTable.test.tsx
│   ├── TokenUsageAnalytics.test.tsx
│   └── ProcessingProgressBar.test.tsx
├── common/                # Shared/common components
│   ├── LoadingScreen.test.tsx
│   ├── AIResponseRenderer.test.tsx
│   └── Pagination.test.tsx
└── README.md              # This file
```

## 🎯 Testing Strategy

### Component Categories

1. **UI Components (Atoms)** - Basic building blocks
   - Button variants, states, and interactions
   - Input fields with validation and icons
   - Themed components for dark/light mode

2. **Chat Components (Molecules)** - Chat functionality
   - Message input with auto-resize and send logic
   - Message display with formatting
   - Chat history and session management

3. **Dashboard Components (Organisms)** - Complex admin features
   - Data tables with sorting and pagination
   - Analytics charts and metrics
   - Document management interfaces

4. **Common Components** - Shared utilities
   - Loading states and animations
   - Layout components
   - Utility components

### Testing Patterns

Each component test follows a consistent structure:

```typescript
describe('ComponentName', () => {
  describe('Rendering', () => {
    // Basic rendering tests
  })

  describe('Props & Variants', () => {
    // Different prop combinations
  })

  describe('User Interactions', () => {
    // Click, keyboard, form interactions
  })

  describe('State Management', () => {
    // Component state changes
  })

  describe('Accessibility', () => {
    // ARIA attributes, keyboard navigation
  })

  describe('Edge Cases', () => {
    // Error states, boundary conditions
  })
})
```

## 🛠 Testing Features

### 1. Comprehensive Coverage
- **Rendering**: Basic component rendering and prop variations
- **Interactions**: User events, keyboard navigation, form submissions
- **States**: Loading, error, disabled, and various component states
- **Accessibility**: ARIA attributes, screen reader compatibility
- **Theming**: Light/dark mode support and responsive design

### 2. Advanced Testing Techniques
- **User Event Simulation**: Realistic user interactions using `@testing-library/user-event`
- **Mock Management**: Sophisticated mocking of external dependencies
- **Async Testing**: Proper handling of async operations and state updates
- **Context Testing**: Testing components within React contexts (Theme, Auth, Language)

### 3. Quality Assurance
- **Visual Regression**: Testing component appearance and styling
- **Performance**: Ensuring components render efficiently
- **Error Boundaries**: Graceful error handling
- **Cross-browser Compatibility**: Consistent behavior across browsers

## 🎨 Component Testing Examples

### Basic UI Component
```typescript
// Button.test.tsx
it('should render primary variant correctly', () => {
  render(<Button variant="primary">Primary</Button>)
  
  const button = screen.getByRole('button')
  expect(button).toHaveClass('bg-green-500', 'hover:bg-green-600', 'text-white')
})
```

### Interactive Component
```typescript
// ChatInput.test.tsx
it('should send message on Enter key', async () => {
  const user = userEvent.setup()
  const onSendMessage = vi.fn()
  
  render(<ChatInput onSendMessage={onSendMessage} />)
  
  const textarea = screen.getByTestId('chat-input')
  await user.type(textarea, 'Hello World')
  await user.keyboard('{Enter}')
  
  expect(onSendMessage).toHaveBeenCalledWith('Hello World')
})
```

### Theme-aware Component
```typescript
// LoadingScreen.test.tsx
it('should render dark theme correctly', () => {
  mockThemeContext.theme = 'dark'
  
  render(<LoadingScreen />)
  
  const title = screen.getByText('APEX')
  expect(title).toHaveClass('text-green-400')
})
```

## 🚀 Running Component Tests

### Run all component tests
```bash
npm test tests/components
```

### Run specific component category
```bash
npm test tests/components/ui
npm test tests/components/Chat
npm test tests/components/Dashboard
```

### Run specific component
```bash
npm test Button.test.tsx
npm test ChatInput.test.tsx
```

### Watch mode for development
```bash
npm test tests/components -- --watch
```

## 📊 Coverage Goals

- **Line Coverage**: > 85%
- **Branch Coverage**: > 80%
- **Function Coverage**: > 90%
- **Statement Coverage**: > 85%

## 🔄 Integration with Phase 1

This component testing suite builds upon the Phase 1 infrastructure:

- **MSW Handlers**: API mocking for components that make HTTP requests
- **Test Factories**: Realistic test data for complex components
- **Test Utils**: Custom render functions with providers
- **Setup Configuration**: Global mocks and environment setup

## 📈 Phase 3 Preparation

These component tests prepare for Phase 3 (Service Testing) by:

- Testing service integration points
- Validating data flow through components
- Ensuring proper error handling
- Documenting component APIs and contracts

## 🎯 Best Practices

1. **Test Behavior, Not Implementation**: Focus on what users see and do
2. **Realistic User Interactions**: Use `userEvent` for authentic interactions
3. **Accessibility First**: Include accessibility tests in every component
4. **Error Scenarios**: Test edge cases and error states
5. **Performance Awareness**: Avoid unnecessary re-renders in tests
6. **Documentation**: Keep tests readable and well-documented

## 🐛 Debugging Tips

1. **Use `screen.debug()`**: Inspect rendered DOM in tests
2. **Check Query Priorities**: Use Testing Library's query guidelines
3. **Async Issues**: Ensure proper `await` usage for user events
4. **Mock Verification**: Verify mocks are working as expected
5. **Coverage Reports**: Use coverage to identify untested paths

## 🔮 Future Enhancements

- **Visual Testing**: Screenshot comparison testing
- **Performance Testing**: Component render performance benchmarks
- **Cross-browser Testing**: Automated testing across different browsers
- **Component Documentation**: Storybook integration for component examples
- **Accessibility Auditing**: Automated a11y testing integration 