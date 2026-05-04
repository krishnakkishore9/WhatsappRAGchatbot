# Phase 4: WhatsApp Webhook & Messaging

## 🎯 Objective
Connect the system to WhatsApp via WasenderAPI by implementing a webhook handler.

## 📝 Tasks
- [ ] Implement `POST /webhook/whatsapp` endpoint.
- [ ] Logic to parse WasenderAPI payload (sender, message).
- [ ] Integration with `RAGService` and `LLMManager`.
- [ ] Implement outgoing message logic using WasenderAPI.
- [ ] Store all incoming and outgoing messages in Supabase.

## ✅ Success Criteria
- [ ] Webhook successfully receives and logs messages.
- [ ] Automated responses are triggered and sent back (verified via mock or real API).
- [ ] Conversation history is correctly tracked in the database.
