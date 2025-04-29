# Environment Configuration for Afeka ChatBot

This document explains the environment variables configuration used in the Afeka ChatBot project.

## Environment Files

The project uses `.env` files to manage environment variables. There are two main files:

1. `.env` - The main environment file with actual configuration values
2. `.env-example` - A template file with placeholder values for reference

## Environment Variable Categories

### Supabase Configuration
These variables are used to connect to the Supabase backend:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
```

- `SUPABASE_URL`: The URL of your Supabase project
- `SUPABASE_KEY`: Your Supabase anonymous key (same as SUPABASE_ANON_KEY)
- `SUPABASE_ANON_KEY`: Your Supabase anonymous key for public operations
- `SUPABASE_SERVICE_KEY`: Your Supabase service key for admin operations (required for user management tests)

### Service URLs
Used for inter-service communication:

```
VITE_BACKEND_URL=http://localhost:8000
API_BASE_URL=http://localhost:8000
AI_SERVICE_URL=http://localhost:5000
```

- `VITE_BACKEND_URL`: Backend URL used by the frontend (with VITE_ prefix for Vite to expose it)
- `API_BASE_URL`: URL for API requests in test scripts
- `AI_SERVICE_URL`: URL of the AI service

### Development Settings
General settings for development mode:

```
NODE_ENV=development
DEBUG=True
VITE_SKIP_TS_CHECK=true
ENVIRONMENT=development
```

### AI Configuration
Settings for the AI service:

```
GEMINI_API_KEY=your-gemini-api-key
FLASK_DEBUG=True
FLASK_ENV=development
AI_API_RATE_LIMIT=60
AI_MAX_MESSAGE_LENGTH=2000
AI_PORT=5000
AI_HOST=0.0.0.0
```

### API Settings
Backend API configuration:

```
API_RATE_LIMIT=100
MAX_DOCUMENT_SIZE_KB=100
MAX_CHAT_MESSAGE_LENGTH=1000
```

### Other Settings
Miscellaneous configurations:

```
TZ=Asia/Jerusalem
```

- `TZ`: Timezone setting for consistent timestamps

## Setting Up Your Environment

1. Copy the `.env-example` file to create a new `.env` file:
   ```
   cp .env-example .env
   ```

2. Edit the `.env` file with your specific values:
   - Replace placeholder values with actual credentials
   - Adjust settings as needed for your development environment

3. Keep sensitive information secure:
   - Never commit your `.env` file to version control
   - The `.env` file is already in the `.gitignore` file

## Environment Variables in Different Services

The project has multiple services that use these environment variables:

1. **Backend Service** (FastAPI)
   - Loads variables via `dotenv` in `src/backend/core/config.py`

2. **Frontend Service** (Vite/React)
   - Uses Vite's environment variable system (variables with `VITE_` prefix)

3. **AI Service** (Flask)
   - Loads configuration in `src/ai/core/config.py`

4. **Test Scripts**
   - User management tests load environment variables in `test_user_management.py`

## Testing Environment

For testing, especially user management tests, make sure you have the following variables set:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
API_BASE_URL=http://localhost:8000
```

The `run_user_tests.py` script will verify these variables before running tests. 