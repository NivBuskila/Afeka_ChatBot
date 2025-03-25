# Afeka Regulations ChatBot 🤖

An AI-powered chatbot designed to help Afeka College students easily access and understand academic regulations and information.

## 👋 New Team Members - Start Here!

### One-Time Setup Requirements
1. **Install Git**
   - Download and install from [git-scm.com](https://git-scm.com/downloads)
   - If you don't have a GitHub account, create one at [github.com](https://github.com)

2. **Install Node.js**
   - Download and install from [nodejs.org](https://nodejs.org/)
   - Choose LTS version (currently 18.x)

3. **Install Python**
   - Download and install from [python.org](https://python.org)
   - Choose version 3.10 or later
   - Ensure "Add Python to PATH" is checked during installation

4. **Install MongoDB**
   - Download and install from [mongodb.com](https://www.mongodb.com/try/download/community)

### Initial Project Setup (Step by Step)

#### Step 1: Clone the Repository
```bash
# Open terminal/command prompt
# Navigate to your preferred directory
# For example:
cd Desktop

# Clone the repository
git clone https://github.com/NivBuskila/Afeka_ChatBot.git

# Enter project directory
cd Afeka_ChatBot
```

#### Step 2: Frontend Setup
```bash
# Navigate to frontend directory
cd src/frontend

# Install required dependencies
npm install

# Start development server
npm run dev
```
If successful, your browser should open to http://localhost:3000

#### Step 3: Backend Setup
```bash
# Return to root directory (if still in frontend)
cd ../..

# Navigate to backend directory
cd src/backend

# Create virtual environment
# Windows:
python -m venv venv
venv\Scripts\activate

# Mac/Linux:
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload
```
Server should run at http://localhost:8000

### Essential Git Commands

```bash
# Check status of changes
git status

# Add changes
git add .

# Save changes
git commit -m "Description of your changes"

# Get latest changes from server
git pull

# Upload your changes to server
git push

# Create new feature branch
git checkout -b feature/your-feature-name
```

### 🚫 Common Pitfalls to Avoid
1. **Never Work Directly on Main Branch**
   - Always create a new branch for your changes
   
2. **Don't Upload Sensitive Files**
   - No .env files
   - No passwords or API keys
   
3. **Don't Upload Generated Directories**
   - node_modules/
   - venv/
   - __pycache__/

### 📁 Project Structure
```
afeka-chatbot/
├── docs/                      # Documentation
│   └── learning/             # Learning materials
├── src/                      # Source code
│   ├── frontend/            # React (client-side)
│   ├── backend/             # FastAPI (server-side)
│   └── ai/                  # AI components
└── tests/                   # Test files
```

### 👥 Team
- Niv Buskila 
- Omri Roter
- Amitay Manor

### 🆘 Troubleshooting Guide

#### Common Issues and Solutions

1. **"command not found: git/node/python"**
   - Verify tool installation
   - Check system PATH settings

2. **"npm ERR!"**
   - Try deleting node_modules directory
   - Run `npm install` again

3. **Git Issues**
   ```bash
   # If something goes wrong, try:
   git fetch --all
   git reset --hard origin/main
   ```

4. **"ModuleNotFoundError" in Python**
   - Ensure virtual environment is active
   - Reinstall requirements: `pip install -r requirements.txt`

#### Getting Help
1. Check existing Issues
2. Ask in team group
3. Create new Issue with:
   - Problem description
   - Steps to reproduce
   - Complete error message

## 🛠️ Technology Stack

### Frontend
- React
- TypeScript
- Tailwind CSS

### Backend
- Python
- FastAPI
- MongoDB

### AI/ML
- LangChain
- Hugging Face

## 🧪 Development Guidelines

### Code Style
1. **Frontend (React/TypeScript)**
   ```typescript
   // Use functional components
   const ChatMessage: React.FC<MessageProps> = ({ content }) => {
     return <div className="p-4">{content}</div>;
   };

   // Type everything
   interface MessageProps {
     content: string;
     timestamp: Date;
   }
   ```

2. **Backend (Python/FastAPI)**
   ```python
   # Use type hints
   from typing import Optional

   async def process_message(content: str) -> dict:
       return {"response": content}
   ```

### Git Workflow
1. Create feature branch
2. Make changes
3. Test locally
4. Create pull request
5. Wait for review

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
