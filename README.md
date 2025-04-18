# Afeka Regulations ChatBot 🤖

An AI-powered chatbot designed to help Afeka College students easily access and understand academic regulations and information.

## 🐳 Docker Quickstart

The easiest way to run the entire application is using Docker Compose:

```bash
# Set Supabase key environment variable (required)
export SUPABASE_KEY=your_key_here  # Linux/Mac
# OR
$env:SUPABASE_KEY="your_key_here"  # Windows PowerShell

# Start all services
docker-compose up -d

# For development environment with hot reloading
docker-compose -f docker-compose.dev.yml up -d
```

Access the application:
- Frontend: http://localhost:80 (production) or http://localhost:5173 (development)
- Backend API: http://localhost:8000
- AI Service: http://localhost:5000

### Docker Commands

```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs frontend
docker-compose logs backend
docker-compose logs ai-service

# Rebuild specific service
docker-compose build frontend

# Stop all services
docker-compose down

# Cleanup everything
docker-compose down --rmi all --volumes
```

## 👋 New Team Members - Start Here!

### One-Time Setup Requirements

1. **Install Docker and Docker Compose**
   - Download from [docker.com](https://www.docker.com/products/docker-desktop/)
   - Verify installation: `docker --version` and `docker-compose --version`

2. **Install Git**
   - Download from [git-scm.com](https://git-scm.com/downloads)

3. **Get Supabase Access**
   - Request access key from team lead
   - Set as environment variable before running Docker

### Manual Setup (Alternative to Docker)

#### Frontend Setup
```bash
cd src/frontend
npm install
npm run dev
```

#### Backend Setup
```bash
cd src/backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

#### AI Service Setup
```bash
cd src/ai
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python app.py
```

## 📁 Project Structure
```
afeka-chatbot/
├── docker-compose.yml       # Production Docker configuration
├── docker-compose.dev.yml   # Development Docker configuration
├── nginx.conf              # Nginx reverse proxy configuration
├── docs/                   # Documentation
├── src/                    # Source code
│   ├── frontend/          # React frontend (TypeScript)
│   │   ├── src/           # Application source
│   │   └── Dockerfile     # Frontend Docker config
│   ├── backend/           # FastAPI backend
│   │   ├── main.py        # Main application entry
│   │   └── Dockerfile     # Backend Docker config
│   ├── ai/                # AI service
│   │   ├── app.py         # Flask application
│   │   └── Dockerfile     # AI service Docker config
│   └── supabase/          # Supabase configuration
└── tests/                 # Test files
```

## 🛠️ Technology Stack

### Frontend
- React with TypeScript
- Vite for development
- Tailwind CSS for styling
- i18n for internationalization (Hebrew/English)

### Backend
- Python with FastAPI
- Async HTTP with httpx
- Supabase for data storage

### AI Service
- Python with Flask
- NLP capabilities

### Infrastructure
- Docker for containerization
- Nginx as reverse proxy
- Supabase for database and storage

## Git Workflow
1. Create feature branch
2. Make changes
3. Test locally with Docker
4. Create pull request
5. Wait for review

## 👥 Team
- Niv Buskila 
- Omri Roter
- Amitay Manor

## 🆘 Common Issues and Solutions

1. **Supabase Key Error**
   - Ensure SUPABASE_KEY environment variable is set

2. **Services Can't Communicate**
   - Check if all containers are running: `docker-compose ps`
   - Verify network configuration in docker-compose.yml

3. **Frontend Build Issues**
   - TypeScript errors can be bypassed with VITE_SKIP_TS_CHECK=true

4. **"Address Already In Use" Error**
   - Check if port is already in use: `netstat -ano | findstr 8000` (Windows) or `lsof -i :8000` (Mac/Linux)
   - Stop the service using that port

5. **Changes Not Reflecting**
   - In production mode, rebuild container: `docker-compose build frontend`
   - In development mode, changes should apply automatically

## 📱 Contact
- Technical questions: Create an Issue
- Urgent matters: [Team Lead Contact]

## 📚 Learning Resources
- [React Official Guide](https://react.dev)
- [TypeScript for Beginners](https://www.typescriptlang.org/docs/handbook/typescript-from-scratch.html)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Git Basics](https://www.atlassian.com/git/tutorials/what-is-version-control)

## ⚡ Quick Start Tips
1. Start with basic technology learning
2. Read existing code to understand structure
3. Make small changes first
4. Ask questions when needed - no question is silly!

## 🧪 Testing
- Write tests for new features
- Run existing tests before pushing
- Use `npm test` for frontend
- Use `pytest` for backend

## 📦 Deployment
- Frontend builds with `npm run build`
- Backend deploys with uvicorn
- MongoDB should be running

## 🔄 CI/CD
- Automatic tests run on push
- Review required for merging
- Automatic deployment on main branch

---
💡 Remember: Everyone was a beginner once. Don't hesitate to ask questions!

## Docker Setup and Usage

### Prerequisites
- Docker and Docker Compose installed
- Git (to clone the repository)

### Setup Instructions

1. Clone the repository
```bash
git clone [repository-url]
cd Afeka_ChatBot
```

2. Configure environment variables
```bash
# The .env file is already configured with Supabase URL 
# You only need to add your Supabase anon key
```
Edit the `.env` file and replace `your_supabase_anon_key_here` with your actual Supabase anon key.

3. Build and start the Docker containers
```bash
docker-compose up --build
```

4. Access the application
- Frontend: http://localhost:80
- Backend API (Python): http://localhost:8000
- AI Service: http://localhost:5000

### Development Mode

For development with hot-reloading and volume mounts:

```bash
docker-compose -f docker-compose.dev.yml up --build
```

This configuration mounts local directories to containers, allowing real-time code changes without rebuilding containers.

In development mode the frontend will be available on http://localhost:3000 instead of port 80.

### Troubleshooting Common Issues

#### Frontend Build Errors
The system is configured to continue working even if there are TypeScript errors. If you need to fix the TypeScript issues:

1. Enter the frontend container:
```bash
docker-compose exec frontend sh
```

2. Run TypeScript checks:
```bash
npm run tsc
```

#### AI Service Issues
If you experience issues with the AI service, try these steps:

1. Check service logs:
```bash 
docker-compose logs ai-service
```

2. Restart just the AI service:
```bash
docker-compose restart ai-service
```

#### Communication Between Services
If services can't communicate with each other:
- Backend->AI: Check that AI_SERVICE_URL is set to "http://ai-service:5000"
- Frontend->Backend: Verify that VITE_BACKEND_URL is set correctly

### Additional Commands

#### Run in detached mode
```bash
docker-compose up -d
```

#### View logs
```bash
docker-compose logs -f
```

#### Stop containers
```bash
docker-compose down
```

#### Access container shell
```bash
# For Python containers (backend, ai-service)
docker-compose exec backend sh
docker-compose exec ai-service sh

# For Node.js container (frontend)
docker-compose exec frontend sh
```

#### Remove volumes (will delete persistent data)
```bash
docker-compose down -v
```

## Project Structure
- `frontend/`: Web interface (React/TypeScript)
- `backend/`: API and business logic (Python/FastAPI)
- `ai/`: AI models and processing (Python/Flask)
- `supabase/`: Database schema and migrations

## Technology Stack in Docker Environment
- Frontend: React with TypeScript, Vite, Tailwind CSS
- Backend: Python with FastAPI
- AI Service: Python with Flask
- Database: Supabase

## Supabase Configuration

The application is configured to connect to Supabase at:
```
https://cqvicgimmzrffvarlokq.supabase.co
```

### Existing Tables
The following tables exist in the Supabase database:
- `document_analytics`: Analytics data for document interactions
- `documents`: Main document storage
- `documents_with_logging`: Documents with additional logging information
- `security_events`: Security-related events
- `users`: User information and permissions

If you need to access conversation history, ensure you add a `conversations` table with the following schema:
- `id`: UUID (primary key)
- `user_id`: String
- `message`: Text
- `response`: JSON
- `created_at`: Timestamp with time zone

## API Endpoints

### Backend (FastAPI)
- `GET /health`: Health check
- `POST /api/chat`: Process chat messages
- `GET /api/documents`: Get documents
- `POST /api/documents`: Create a new document

### AI Service (Flask)
- `GET /health`: Health check
- `POST /analyze`: Analyze text input

## Future Enhancements

### RAG (Retrieval Augmented Generation) Implementation

The system is designed with placeholders for a future RAG implementation that will provide accurate responses based on institutional documents:

1. **Document Storage**: Already implemented through Supabase, allowing admin users to upload regulatory documents
2. **AI Service**: Currently provides basic placeholder responses, but designed to be extended with RAG capabilities
3. **Frontend Integration**: UI already set up for chat interactions with backend API

When implemented, the RAG system will:
- Extract knowledge from uploaded documents 
- Build semantic vector representations of document content
- Match user queries to the most relevant document sections
- Generate accurate, context-aware responses based on the institution's own documentation

This approach will ensure that responses are factually accurate, up-to-date, and specific to the institution's regulations without requiring constant manual updates to response templates.
