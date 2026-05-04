# Phase 1: Project Setup & Database

## 🎯 Objective
Initialize the project structure, configure environment variables, and set up the Supabase database schema.

## 📝 Tasks
- [ ] Initialize FastAPI project structure.
- [ ] Create `.env` file with placeholders for all API keys.
- [ ] Set up Supabase project.
- [ ] Create database tables in Supabase:
    - `conversations` (ID, phone_number, created_at)
    - `messages` (ID, conversation_id, role, content, created_at)
    - `documents` (ID, filename, status, file_url, created_at)
- [ ] Initialize Python virtual environment and install base dependencies (`fastapi`, `uvicorn`, `supabase`, `python-dotenv`).

## ✅ Success Criteria
- [ ] FastAPI app runs locally with a `/health` endpoint.
- [ ] Supabase connection is verified.
- [ ] All tables are visible in the Supabase dashboard.
