# 🚀 AI Development Prompts: WhatsappRAGChatbot

This document contains a sequence of prompts designed to guide an AI through the step-by-step development of the AI-Powered WhatsApp RAG Chatbot.

> [!IMPORTANT]
> **Rule for the AI**: After completing each phase, you MUST stop and ask the user for approval before proceeding to the next prompt.

---

### Phase 1: Project Setup & Database
**Prompt:**
> "Initialize a FastAPI project for the WhatsappRAGChatbot. Create a basic directory structure including `services/`, `models/`, and `static/`. Set up a `.env` file with placeholders for `OPENAI_API_KEY`, `PINECONE_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`, and `WASENDER_API_KEY`. Using the `supabase-mcp-server`, create the following tables in Supabase:
> 1. `conversations`: `id` (UUID, PK), `phone_number` (text), `created_at` (timestamp).
> 2. `messages`: `id` (UUID, PK), `conversation_id` (UUID, FK), `role` (text), `content` (text), `created_at` (timestamp).
> 3. `documents`: `id` (UUID, PK), `filename` (text), `status` (text), `file_url` (text), `created_at` (timestamp).
> Finally, create a `main.py` with a simple `/health` endpoint and verify the Supabase connection."

---

### Phase 2: Document Processing & Vector Storage
**Prompt:**
> "Implement the document processing pipeline. Create a `DocumentProcessor` service in `services/doc_processor.py` that:
> 1. Extracts text from uploaded PDF or TXT files.
> 2. Splits text into chunks using a recursive character splitter (size 1000, overlap 200).
> 3. Generates embeddings for each chunk using OpenAI's `text-embedding-3-small`.
> 4. Upserts the vectors into a Pinecone index named `txstate-rag` with metadata (text, filename).
> Create an API endpoint `POST /admin/upload` that receives a file, saves it to Supabase storage (or locally for now), and triggers this processing pipeline. Update the `documents` table status accordingly."

---

### Phase 3: RAG Implementation & AI Fallback
**Prompt:**
> "Develop the core RAG logic. Create a `RAGService` in `services/rag_service.py` to:
> 1. Embed user queries.
> 2. Search Pinecone for the top 3 relevant chunks.
> 3. Aggregate chunks into a context string.
> Then, create an `LLMManager` in `services/llm_manager.py` that calls OpenAI's `gpt-4o-mini`. Implement a fallback mechanism: if OpenAI fails, use the Hugging Face Inference API. Use the 'Bob' persona (TX State Admission Assistant) in the system prompt. Verify this works with a test script that queries the RAG system."

---

### Phase 4: WhatsApp Webhook & Messaging
**Prompt:**
> "Implement the WhatsApp integration. Create a `POST /webhook/whatsapp` endpoint in `main.py` to handle incoming payloads from WasenderAPI. The logic should:
> 1. Identify the user by phone number and upsert them into the `conversations` table.
> 2. Pass the user's message to the `RAGService`.
> 3. Log the user's message and the assistant's response in the `messages` table.
> 4. Send the assistant's response back to the user via WasenderAPI's `send-message` endpoint.
> Ensure robust error handling for API failures."

---

### Phase 5: Simple Admin UI
**Prompt:**
> "Create a minimal Admin Panel. In the `static/` folder, create an `index.html` file using Vanilla HTML/CSS/JS (you can use a simple CSS framework like Bootstrap via CDN). The UI should include:
> 1. A file upload section for new documents.
> 2. A table showing indexed documents and their status.
> 3. A scrollable 'Recent Logs' section that fetches and displays the latest entries from the `messages` table.
> Update `main.py` to serve these static files at the root `/admin` path."

---

### Phase 6: Final Integration & Deployment
**Prompt:**
> "Prepare for deployment. Create a `vercel.json` file to configure the FastAPI app for Vercel Serverless Functions. Ensure all dependencies are in `requirements.txt`. Perform a final end-to-end test: upload a document, simulate a WhatsApp message via the webhook, and verify the response and logs. Provide a final summary of the deployment steps including environment variable setup in Vercel."
