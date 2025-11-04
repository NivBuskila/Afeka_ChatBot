# APEX Afeka ChatBot 

A smart, AI-powered chatbot system designed to assist students at Afeka College of Engineering in obtaining quick and accurate information regarding academic regulations, procedures, and relevant institutional data.

## Features

The APEX Afeka ChatBot is a comprehensive solution built on a modern microservices architecture, offering the following key features:

*   **Intelligent Chatbot:** Provides tailored and accurate responses using **Retrieval-Augmented Generation (RAG)** techniques.
*   **Document Management:** Allows for the upload, management, and processing of academic documents to serve as the knowledge base.
*   **Admin Dashboard:** An advanced interface for system administrators with built-in analytics and system control.
*   **Multilingual Support:** Full support for both **Hebrew and English** languages.
*   **Advanced Security:** User authentication and access control managed via **Supabase**.
*   **Responsive Design:** User interface optimized for all device types.
*   **High Performance:** Microservices architecture designed for high load and scalability.

## System Architecture

The system employs a microservices architecture with a clear separation of concerns across layers:

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | `React`, `TypeScript`, `Vite`, `Tailwind CSS` | The user interface, providing the chat experience and the admin dashboard. |
| **Backend (API Gateway)** | `FastAPI` (Python), `Pydantic`, `AsyncIO` | The main API layer, handling business logic, data validation, and orchestrating the AI/RAG processes. |
| **AI Processing** | `LangChain`, `Google Generative AI` (Gemini) | Core AI logic for RAG, document embedding, and chat response generation. Integrated within the FastAPI backend. |
| **Database & Storage** | `Supabase` (`PostgreSQL`, `Auth`, `Storage`) | Provides the relational database, user authentication, file storage for documents, and Row Level Security (RLS). |
| **Vector Store** | `Postgres` with `pgvector` (via Supabase) | Used for storing document embeddings and facilitating efficient vector search for the RAG process. |
| **Infrastructure** | `Docker` & `Docker Compose`, `Nginx` | Containerization for easy deployment and a reverse proxy for serving the application. |

## Technologies Used

### Frontend (`src/frontend`)

*   **Framework:** React 18.3.1
*   **Language:** TypeScript 5.7.3
*   **Build Tool:** Vite
*   **Styling:** Tailwind CSS
*   **State/Routing:** React Router, React Context
*   **Internationalization:** `i18next`, `react-i18next`
*   **Data Visualization:** `recharts`
*   **API Client:** `@supabase/supabase-js`

### Backend (`src/backend`)

*   **Framework:** FastAPI 0.103.0+
*   **Language:** Python 3.11+
*   **Data Validation:** Pydantic 2.0.0+
*   **AI/RAG:** LangChain, Google Generative AI (Gemini), `tiktoken`
*   **Database Drivers:** `psycopg2-binary`, `asyncpg`, `langchain-postgres`
*   **Document Processing:** `pypdf2`, `python-docx`, `unstructured`

### AI Service (`src/ai`)

*   **Framework:** Flask
*   **Purpose:** Minimal service retained primarily for health checks and API key management status. **Note:** The main RAG/Chat logic has been migrated to the `src/backend` service.

##  Quick Start

The recommended way to run the project is using Docker Compose.

### Prerequisites

*   **Docker & Docker Compose**
*   **Git**
*   **Supabase Project:** You will need a Supabase project URL and a service role key.

### 1. Clone the Repository

```bash
git clone https://github.com/NivBuskila/Afeka_ChatBot.git
cd Afeka_ChatBot
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory based on the provided `.env.example`.

```bash
# .env file example
# --- Supabase Configuration ---
SUPABASE_URL="YOUR_SUPABASE_PROJECT_URL"
SUPABASE_SERVICE_KEY="YOUR_SUPABASE_SERVICE_ROLE_KEY"
SUPABASE_ANON_KEY="YOUR_SUPABASE_ANON_KEY"

# --- AI Configuration ---
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
# ... other AI-related variables
```

### 3. Run with Docker Compose

Use the production configuration for a standard deployment:

```bash
docker-compose up -d
```

For development with hot-reloading for the frontend and backend services:

```bash
docker-compose -f docker-compose.dev.yml up -d
```

### Access the Application

| Service | Production URL | Development URL | Notes |
| :--- | :--- | :--- | :--- |
| **Frontend** | `http://localhost:80` | `http://localhost:5173` | The main application interface. |
| **Backend API** | `http://localhost:8000` | `http://localhost:8000` | FastAPI service. Documentation available at `/docs`. |
| **AI Service** | `http://localhost:5000` | `http://localhost:5000` | Minimal Flask service for health checks. |

## Project Structure

```
Afeka_ChatBot/
├── src/
│   ├── frontend/                  # React/TypeScript UI (Vite)
│   │   ├── src/
│   │   ├── public/
│   │   └── package.json
│   ├── backend/                   # FastAPI Server (Python)
│   │   ├── app/
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── ai/                        # Minimal Flask AI Service
│   │   ├── services/
│   │   └── app.py
│   └── tests/                     # Automated tests (Backend/Frontend)
├── supabase/                      # Supabase configuration and migrations
├── RAG_Test_Pro/                  # Dedicated RAG testing environment
├── docker-compose.yml             # Production Docker configuration
├── docker-compose.dev.yml         # Development Docker configuration
├── .env.example                   # Template for environment variables
└── README.md                      # This file
```

## Contributing

We welcome contributions! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## Development Team

The project was developed by:

*   [Niv Buskila](https://github.com/NivBuskila)
*   [Amitay Manor](https://github.com/AmitayManor)
*   [Omri Roter](https://github.com/OmriRoter)

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
