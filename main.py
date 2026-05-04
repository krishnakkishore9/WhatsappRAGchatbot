import os
import shutil
import httpx
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from supabase import create_client, Client
from dotenv import load_dotenv
from services.doc_processor import DocumentProcessor
from services.rag_service import RAGService
from services.llm_manager import LLMManager

load_dotenv(override=True)

app = FastAPI(title="WhatsappRAGChatbot")

# Services
doc_processor = DocumentProcessor()
rag_service = RAGService()
llm_manager = LLMManager()

# Supabase Setup
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key) if url and key else None

@app.get("/")
async def root():
    return {"message": "WhatsApp RAG Chatbot is running! Send a POST request to /webhook/whatsapp to interact."}

@app.get("/health")
async def health_check():
    status = "healthy"
    db_status = "connected" if supabase else "not configured"
    
    if supabase:
        try:
            # Simple query to verify connection
            supabase.table("conversations").select("count", count="exact").limit(1).execute()
        except Exception as e:
            db_status = f"error: {str(e)}"
            status = "unhealthy"
            
    return {
        "status": status,
        "database": db_status
    }

@app.post("/admin/upload")
async def upload_document(file: UploadFile = File(...)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    
    # 1. Save file locally
    upload_path = os.path.join("uploads", file.filename)
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # 2. Register in Supabase
        doc_data = {
            "filename": file.filename,
            "status": "processing"
        }
        res = supabase.table("documents").insert(doc_data).execute()
        doc_id = res.data[0]["id"]
        
        # 3. Process and Index
        chunks_count = doc_processor.process_and_index(upload_path, doc_id)
        
        # 4. Update status
        supabase.table("documents").update({"status": "indexed"}).eq("id", doc_id).execute()
        
        return {
            "message": "Document indexed successfully",
            "document_id": doc_id,
            "chunks": chunks_count
        }
    except Exception as e:
        # Update status to error if possible
        if 'doc_id' in locals():
            supabase.table("documents").update({"status": f"error: {str(e)}"}).eq("id", doc_id).execute()
        raise HTTPException(status_code=500, detail=str(e))

async def process_webhook(sender: str, sender_jid: str, user_message: str):
    try:
        # 1. Upsert Conversation
        conv_res = supabase.table("conversations").upsert(
            {"phone_number": sender}, on_conflict="phone_number"
        ).execute()
        conversation_id = conv_res.data[0]["id"]
        
        # 2. Log User Message
        supabase.table("messages").insert({
            "conversation_id": conversation_id,
            "role": "user",
            "content": user_message
        }).execute()
        
        # 3. RAG Process
        context = rag_service.get_context(user_message)
        assistant_response = await llm_manager.generate_response(user_message, context)
        
        # 4. Log Assistant Response
        supabase.table("messages").insert({
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": assistant_response
        }).execute()
        
        # 5. Send back via WasenderAPI
        wasender_key = os.getenv("WASENDER_API_KEY")
        wasender_url = "https://www.wasenderapi.com/api/send-message"
        
        async with httpx.AsyncClient() as client:
            send_res = await client.post(
                wasender_url,
                headers={"Authorization": f"Bearer {wasender_key}"},
                json={
                    "to": sender_jid,
                    "text": assistant_response
                },
                timeout=10.0
            )
            print(f"WasenderAPI Response: {send_res.status_code} - {send_res.text}")
            
    except Exception as e:
        print(f"Background Process Error: {str(e)}")

@app.post("/webhook/whatsapp")

async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase not configured")
    
    payload = await request.json()
    print(f"Webhook Received: {payload}")
    
    event_type = payload.get("event", "")
    
    # Only handle incoming messages
    if event_type != "messages.received":
        return {"status": "ignored", "reason": f"event '{event_type}' not handled"}
    
    # Real WasenderAPI structure: data -> messages -> ...
    messages_data = payload.get("data", {}).get("messages", {})
    
    # Sender: use cleanedSenderPn for our DB, senderPn for replying
    key_data = messages_data.get("key", {})
    sender = key_data.get("cleanedSenderPn", "")
    if sender:
        sender = f"+{sender}"
    # WasenderAPI needs the full JID format (e.g. 916300986658@s.whatsapp.net)
    sender_jid = key_data.get("senderPn", sender)
    
    # Message text: use messageBody (simplest field)
    user_message = (
        messages_data.get("messageBody") or
        messages_data.get("message", {}).get("conversation") or
        ""
    )
    
    # Ignore messages sent by the bot itself
    from_me = messages_data.get("key", {}).get("fromMe", False)
    if from_me:
        return {"status": "ignored", "reason": "own message"}

    if not sender or not user_message:
        return {"status": "ignored", "reason": "missing sender or message text"}
    
    # Add to background tasks and return immediately
    background_tasks.add_task(process_webhook, sender, sender_jid, user_message)
    
    return {"status": "success", "message": "processing started in background"}


@app.get("/admin/documents")
async def list_documents():
    if not supabase:
        return []
    res = supabase.table("documents").select("*").order("created_at", desc=True).execute()
    return res.data

@app.get("/admin/logs")
async def list_logs():
    if not supabase:
        return []
    # Fetch recent messages with conversation details
    res = supabase.table("messages").select("*, conversations(phone_number)").order("created_at", desc=True).limit(50).execute()
    return res.data

# Serve Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/admin")
async def admin_page():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
