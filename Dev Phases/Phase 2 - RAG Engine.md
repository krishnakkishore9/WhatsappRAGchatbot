# Phase 2: Document Processing & Vector Storage

## 🎯 Objective
Implement the logic to process documents (PDF/Text) and index them into the Pinecone vector database.

## 📝 Tasks
- [ ] Initialize Pinecone index (`txstate-rag`).
- [ ] Implement `DocumentProcessor` service:
    - PDF/Text extraction logic.
    - Chunking strategy (RecursiveCharacterTextSplitter).
    - Embedding generation using OpenAI `text-embedding-3-small`.
- [ ] Create `/admin/upload` endpoint to handle file uploads.
- [ ] Implement logic to store document metadata in Supabase and vectors in Pinecone.

## ✅ Success Criteria
- [ ] A test PDF can be uploaded via API.
- [ ] Chunks are correctly stored in Pinecone with metadata.
- [ ] Document status updates to 'indexed' in Supabase.
