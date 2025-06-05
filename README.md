# Afeka ChatBot

## מבנה הפרויקט

הפרויקט מאורגן במבנה התיקיות הבא:

```
afeka-chatbot/
├── config/               # קבצי תצורה וסביבה
│   ├── .env              # הגדרות סביבה פעילות
│   └── .env.example      # דוגמה להגדרות סביבה
├── docker/               # קבצי Docker
│   ├── docker-compose.yml        # הגדרות Docker לסביבת ייצור
│   ├── docker-compose.dev.yml    # הגדרות Docker לסביבת פיתוח
│   └── nginx.conf                # קונפיגורציית Nginx
├── scripts/              # סקריפטי הפעלה
│   ├── run_full_project.bat      # הפעלת הפרויקט המלא
│   ├── run_frontend.bat          # הפעלת הפרונטאנד בלבד
│   ├── run_chat_gui.bat          # הפעלת ממשק צ'אט גרפי
│   └── run_gemini_test.bat       # בדיקת חיבור ל-Gemini API
├── src/                  # קוד המקור
│   ├── ai/               # שירות ה-AI
│   ├── backend/          # שירות הבקאנד
│   ├── frontend/         # ממשק המשתמש
│   ├── config/           # קבצי קונפיגורציה פנימיים
│   └── supabase/         # קבצים הקשורים ל-Supabase
├── data/                 # נתונים וקבצי מידע
├── docs/                 # תיעוד הפרויקט
├── tests/                # בדיקות
└── run.bat               # סקריפט הפעלה מרכזי
```

## הפעלה מהירה

הדרך הקלה ביותר להריץ את הפרויקט היא באמצעות סקריפט ההפעלה המרכזי:

```
run.bat
```

סקריפט זה יציג תפריט המאפשר לבחור את המרכיב שברצונך להפעיל.

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
├── config/               # קבצי תצורה וסביבה
│   ├── .env              # הגדרות סביבה פעילות
│   └── .env.example      # דוגמה להגדרות סביבה
├── docker/               # קבצי Docker
│   ├── docker-compose.yml        # הגדרות Docker לסביבת ייצור
│   ├── docker-compose.dev.yml    # הגדרות Docker לסביבת פיתוח
│   └── nginx.conf                # קונפיגורציית Nginx
├── scripts/              # סקריפטי הפעלה
│   ├── run_full_project.bat      # הפעלת הפרויקט המלא
│   ├── run_frontend.bat          # הפעלת הפרונטאנד בלבד
│   ├── run_chat_gui.bat          # הפעלת ממשק צ'אט גרפי
│   └── run_gemini_test.bat       # בדיקת חיבור ל-Gemini API
├── src/                  # קוד המקור
│   ├── ai/               # שירות ה-AI
│   ├── backend/          # שירות הבקאנד
│   ├── frontend/         # ממשק המשתמש
│   ├── config/           # קבצי קונפיגורציה פנימיים
│   └── supabase/         # קבצים הקשורים ל-Supabase
├── data/                 # נתונים וקבצי מידע
├── docs/                 # תיעוד הפרויקט
├── tests/                # בדיקות
└── run.bat               # סקריפט הפעלה מרכזי

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

## Developer Setup Guide

This guide will help you set up the Afeka ChatBot project on your local machine for development.

### Prerequisites

1. **Node.js** (v18 or later)
2. **Python** (v3.10 or later)
3. **Git**
4. **Supabase** account (for database access)

### Getting Started

#### Clone the Repository

1. Open a terminal and run:

   ```bash
   git clone https://github.com/your-org/afeka-chatbot.git
   cd afeka-chatbot
   ```

2. Checkout the development branch:
   ```bash
   git checkout "Omri's"
   ```
   Note: The quotes are important due to the apostrophe in the branch name.

#### Backend Setup

1. Create and activate a Python virtual environment:

   ```bash
   # Windows
   python -m venv backend_venv
   backend_venv\Scripts\activate

   # macOS/Linux
   python -m venv backend_venv
   source backend_venv/bin/activate
   ```

2. Install Python dependencies:

   ```bash
   cd src/backend
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the `src/backend` directory
   - Add the following variables (replace with actual values):
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   OPENAI_API_KEY=your_openai_api_key
   ```

#### Frontend Setup

1. Install Node.js dependencies:

   ```bash
   cd src/frontend
   npm install
   ```

2. Set up environment variables:
   - Create a `.env` file in the `src/frontend` directory
   - Add the following variables (replace with actual values):
   ```
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

### Running the Application

#### Option 1: Run Frontend and Backend Separately

1. **Backend**:

   ```bash
   # From the project root, with virtual environment activated
   cd src/backend
   python app.py
   ```

   The backend will be available at `http://localhost:5000`

2. **Frontend**:
   ```bash
   # In a new terminal
   cd src/frontend
   npm run dev
   ```
   The frontend will be available at `http://localhost:5174`

#### Option 2: Use the Batch Scripts (Windows Only)

For convenience, you can use the included batch scripts:

1. To run the frontend only:

   ```
   run_frontend.bat
   ```

2. To run both frontend and backend:
   ```
   run_full_project.bat
   ```

### Working with Translations

The application supports both English and Hebrew:

- Translation files are located in `src/frontend/src/i18n/locales/`
- When adding new text to the UI, ensure you add the translations to both language files
- Use direct translation values (not translation keys) in components that show language keys

### Version Control Guidelines

1. Create a new branch for each feature:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Commit messages should be in English and descriptive

3. Before pushing, ensure your code is properly formatted and lint-free

4. Push to your branch and create a pull request to the main development branch

### Troubleshooting

If you encounter any issues:

1. Ensure all dependencies are installed
2. Check that environment variables are correctly set
3. Make sure Supabase is properly configured
4. Restart the development servers

For database-related issues, check the Supabase console for any errors.

### Contact

For questions or access issues, contact the project lead.

## 🧪 Running Tests (Pytest without Virtual Environment)

If you prefer to run `pytest` using your global Python installation (without creating a dedicated virtual environment), follow these steps. This can be useful for quick checks but be mindful of potential global package conflicts.

**1. Install Required Packages:**

Make sure you have `pytest` and other necessary libraries installed globally. If you encounter `ImportError` issues related to `langchain` or other packages during testing, you might need to install or upgrade them:

```bash
python -m pip install --upgrade pip
python -m pip install pytest sentence-transformers langchain langchain-openai langchain_experimental langchain-google-genai python-dotenv
```

_(Adjust the list of packages as needed based on your project's specific test dependencies and any `ImportError` messages you see)._

**2. Configure PYTHONPATH (Important for Module Resolution):**

When running `pytest` from the project root, Python might not be able to find your project's internal modules (e.g., those inside `src/backend` or `src/ai`). To fix `ModuleNotFoundError` issues:

- **For Backend Tests:** If your tests import modules from `src/backend/services` or `src/backend/app`, you need to add `src/backend` to your `PYTHONPATH`.
- **For AI Tests:** Similarly, if tests import from `src/ai`, you might need to adjust `PYTHONPATH`.

Example for PowerShell (when running tests that need `src/backend`):

```powershell
$env:PYTHONPATH = "src\backend"
```

Or for bash/zsh:

```bash
export PYTHONPATH="src/backend"
```

You'll need to set this in your terminal session _before_ running `pytest`.

**3. Run Pytest:**

Once packages are installed and `PYTHONPATH` is set correctly for your context, run `pytest` with verbose output:

```powershell
# Example for backend tests (assuming PYTHONPATH is set as above)
python -m pytest -vv
```

If tests are located in a specific directory (e.g., `tests/backend`), you can target them:

```powershell
python -m pytest -vv tests/backend
```

**Troubleshooting `ImportError: cannot import name 'SemanticChunker' from 'langchain.text_splitter'`:**

This specific error means that the `SemanticChunker` has moved. It's now in `langchain_experimental.text_splitter`. Ensure your code imports it correctly:

```python
# Old, incorrect import:
# from langchain.text_splitter import SemanticChunker

# New, correct import:
from langchain_experimental.text_splitter import SemanticChunker
```

Make sure all files using `SemanticChunker` (like `rag_service.py` and `document_processor.py`) are updated. Also, ensure `langchain_experimental` is installed.

## �� Project Structure

- `frontend/`: Web interface (React/TypeScript)
- `backend/`: API and business logic (Python/FastAPI)
- `ai/`: AI models and processing (Python/Flask)
  - `ai/services/`: RAG and AI business logic
  - `ai/config/`: AI configuration and profiles
  - `ai/scripts/`: Management and utility scripts
- `supabase/`: Database schema and migrations
- `RAG_test/`: AI system testing and validation

## 🔧 AI Configuration Management

The project includes several AI-related management scripts:

### Profile Management

To manage RAG system configuration profiles:

```bash
python src/ai/scripts/manage_profile.py
```

This script allows you to:

- View current AI configuration
- Switch between different performance profiles (fast, balanced, high_quality, etc.)
- Test the current configuration
- List all available profiles

#### Available Profiles

1. **Enhanced Testing (AGGRESSIVE)** ⭐ **[פעיל כברירת מחדל במערכת]**

   - Based on 66.7% failure analysis - AGGRESSIVE PARAMETERS
   - Similarity threshold: 0.15 (extremely low for maximum coverage)
   - Max chunks: 40 (increased from 30)
   - Max context chunks: 25 (increased for complex sections)
   - Chunk size: 600 (smaller for precise section detection)
   - High overlap: 300 tokens (maximum continuity)
   - Semantic/Keyword balance: 0.7/0.3 (better section number detection)
   - Max context: 15,000 tokens (increased for comprehensive answers)
   - Temperature: 0.02 (maximum accuracy)

2. **High Quality** - Maximum accuracy, slower performance
3. **Fast** - Quick responses, good quality
4. **Balanced** - Good balance between speed and accuracy
5. **Improved** - Optimized for missing sections
6. **Debug** - Development and testing with detailed logs

### Testing Scripts

Located in `RAG_test/`:

```bash
# Run comprehensive RAG system tests with profile and question set selection
python RAG_test/test_runner.py

# Quick debugging and profile comparison
python RAG_test/debug_rag.py
```

The test runner now includes:

- **Profile Selection**: Choose which RAG configuration to test
- **Question Set Selection**: Choose from multiple test question sets:
  - Basic RAG Test Set (30 mixed questions)
  - Detailed Accuracy Test Set (30 comprehensive accuracy questions)
- **Comprehensive Reports**: Detailed analysis with profile information
- **Chunking Analysis**: Specific insights into chunk selection and scoring

Test results are saved in `RAG_test/results/` with:

- Detailed text reports with profile and question set information
- JSON raw data for further analysis
- Chunk analysis for debugging retrieval issues
