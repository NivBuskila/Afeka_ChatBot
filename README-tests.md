# Afeka ChatBot Tests

This document describes the test suite for the Afeka ChatBot project and how to run the tests.

## Available Tests

The test suite consists of several test modules:

1. **API Tests**
   - `api_test_extended.py`: Tests the backend API endpoints, including health check, document list, and chat functionality.
   - `simple_api_test.py`: Basic API tests for simple health checks.

2. **Frontend Tests**
   - `frontend_ui_test.py`: Tests the frontend UI accessibility and component presence.

3. **User Management Tests**
   - `test_user_management.py`: Tests user creation, authentication, and deletion for both regular and admin users.

## Running Tests

### Prerequisites

Before running the tests, make sure:

1. The backend service is running on `http://localhost:8000`
2. The frontend service is running on `http://localhost:5173`
3. For user management tests, you need Supabase credentials in a `.env` file:
   - Copy `.env-example` to `.env` and fill in your Supabase credentials

### Running All Tests

To run all tests at once:

```
python run_all_tests.py
```

This will execute all available tests and provide a summary of results.

### Running Individual Tests

You can run individual test modules separately:

```
# Backend API tests
python api_test_extended.py

# Frontend UI tests
python frontend_ui_test.py

# User Management tests
python run_user_tests.py
```

## User Management Tests

The user management tests verify:

1. Creating a regular user in Supabase
2. Creating an admin user in Supabase
3. Verifying user authentication (login)
4. Testing access to protected resources
5. Verifying logout functionality
6. Proper cleanup of test users

### Configuration

To run user management tests, you need the following environment variables:

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anonymous key for public operations
- `SUPABASE_SERVICE_KEY`: Your Supabase service key for admin operations

You can set these in a `.env` file or as environment variables.

## Test Directory Structure

```
/
├── api_test_extended.py      # Extended API tests
├── frontend_ui_test.py       # Frontend UI tests
├── run_all_tests.py          # Script to run all tests
├── run_user_tests.py         # Script to run user management tests
├── simple_api_test.py        # Simple API tests
├── test_user_management.py   # User management tests
├── .env-example              # Example environment file
└── tests/                    # Additional structured tests
    ├── backend/              # Structured backend tests
    │   ├── api/              # API-specific tests
    │   ├── integration/      # Integration tests
    │   └── services/         # Service-specific tests
    ├── frontend/             # Structured frontend tests
    │   └── components/       # Component-specific tests
    └── ai/                   # AI-specific tests (future)
```

## Adding New Tests

When adding new tests:

1. Create your test file with clear test functions
2. Consider adding the test to `run_all_tests.py`
3. Follow the existing patterns for test execution and reporting
4. Ensure proper cleanup of any resources created during tests

## Best Practices

- Always clean up after tests (delete test users, data, etc.)
- Use randomly generated data where possible (e.g., test emails)
- Skip tests gracefully when resources aren't available
- Provide clear, descriptive error messages
- Separate test logic from test execution scripts 