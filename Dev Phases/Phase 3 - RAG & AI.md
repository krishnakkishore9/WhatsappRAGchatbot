# Phase 3: RAG Implementation & LLM Fallback

## 🎯 Objective
Develop the core retrieval logic and integrate AI models with fallback capabilities.

## 📝 Tasks
- [ ] Implement `RAGService`:
    - Query embedding generation.
    - Pinecone semantic search.
    - Context aggregation.
- [ ] Implement `LLMManager`:
    - Integration with OpenAI Chat Completion.
    - Fallback logic to Hugging Face Inference API.
    - Prompt engineering for "Bob" (University Assistant persona).
- [ ] Create a local test script to verify the full RAG pipeline (Query -> Context -> Answer).

## ✅ Success Criteria
- [ ] System generates accurate answers based on uploaded documents.
- [ ] Fallback to Hugging Face works when OpenAI is simulated to fail.
- [ ] The "Bob" persona and TX State context are correctly applied.
