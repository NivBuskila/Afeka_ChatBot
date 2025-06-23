# Afeka ChatBot - Frontend

This document provides specific information about the frontend service of the Afeka ChatBot application.

For general project setup, installation, and running instructions (including Docker and manual setup for the frontend), please refer to the main [README.md](../../README.md) file in the root of the project.

For detailed information on environment variables, including those required for the frontend (prefixed with `VITE_`), please consult the [README-env.md](../../README-env.md) file.

## Project Structure

The frontend source code (`src/`) is organized as follows:

```
src/
  ├── app/               # Main application setup, routing, global state
  ├── assets/            # Static assets (images, fonts)
  ├── components/        # Reusable React components
  │   ├── Chat/          # Components related to the chat interface
  │   ├── Dashboard/     # Components for the admin dashboard
  │   ├── Login/         # Login and authentication components
  │   └── ...            # Other UI components
  ├── config/            # Configuration files (e.g., Supabase client)
  ├── contexts/          # React contexts for global state management
  ├── i18n/              # Internationalization (i18n) files
  │   └── locales/       # Language-specific translation files (en, he)
  ├── services/          # Services for API calls and business logic
  ├── styles/            # Global styles, Tailwind CSS setup
  ├── types/             # TypeScript type definitions
  └── utils/             # Utility functions
```

## Technologies

The frontend is built using the following technologies:

- React
- TypeScript
- Vite (build tool and dev server)
- Tailwind CSS (styling)
- Supabase (for backend interaction)
- i18next (for internationalization)
- React Dropzone (for file uploads)
- Cypress (for E2E testing)

## Key Features

- Document management (upload, download, delete)
- Usage statistics and analytics
- Multilingual support (Hebrew and English)
- Modern, responsive user interface
- Secure authentication and authorization via Supabase

## Development

To start the frontend development server (after initial project setup as described in the main `README.md`):

```bash
# Navigate to the frontend directory
cd src/frontend

# Install dependencies (if not already done)
npm install

# Start the development server
npm run dev
```
The application will typically be available at `http://localhost:5173`.

## Building for Production

To build the frontend application for production:

```bash
# Navigate to the frontend directory
cd src/frontend

# Run the build script
npm run build
```
The production-ready files will be placed in the `dist` directory.
