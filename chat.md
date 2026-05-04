# 🎓 WhatsApp RAG Chatbot: Execution & Learning Guide

Welcome! This guide explains exactly how your AI chatbot works, how to run it, and what happens "under the hood" during each step.

---

## 🚀 1. How to Run the Project Locally

### Step A: Start the Backend
Open your terminal in the project folder and run:
```powershell
python -m uvicorn main:app --reload
```
*   **What happens?** This starts the FastAPI server. The `--reload` flag means the server will automatically restart whenever you save a change to the code.
*   **URL**: Your app is now live at `http://127.0.0.1:8000`.

### Step B: The Admin Dashboard
Go to `http://127.0.0.1:8000/admin`.
*   This is where you manage your knowledge base.
*   When you upload a PDF here, the system triggers the **Indexing Pipeline**.

---

## 🧠 2. The "Under the Hood" Flow

### Phase 1: Ingestion (Uploading Documents)
When you click "Upload" in the Admin UI:
1.  **Text Extraction**: The system reads your PDF/Text file using `pypdf`.
2.  **Chunking**: The text is broken into small pieces (chunks) so the AI can find specific answers easily.
3.  **Embedding**: Each chunk is converted into a list of numbers (a vector) using a local model (`all-MiniLM-L6-v2`).
4.  **Pinecone Storage**: These vectors are saved in your **Pinecone** vector database.
5.  **Supabase Tracking**: The file name and status are saved in your **Supabase** SQL database.

### Phase 2: Retrieval (The "R" in RAG)
When a message arrives from WhatsApp:
1.  **Search**: The user's question is converted into a vector.
2.  **Context Finding**: We ask Pinecone: *"Find the 3 chunks of text that are most similar to this question."*
3.  **Retrieval**: Pinecone returns the actual text from your PDFs.

### Phase 3: Generation (The "G" in RAG)
1.  **The Prompt**: We combine the **Context** + **User Question** into a single message for the AI.
2.  **Fallback Chain**: 
    *   Try **OpenAI** first.
    *   If OpenAI is out of credits, try **Hugging Face**.
    *   If those fail, use your discovered **Gemini 2.5 Flash** model.
3.  **The Answer**: The AI generates a professional response as "Bob".

---

## 📱 3. How to Connect to Real WhatsApp (The Deep Dive)

Connecting to WhatsApp involves three main players: **Your Computer**, **WasenderAPI**, and **The WhatsApp App**.

### Step 1: The "Phone Link"
You first go to your **WasenderAPI Dashboard** and "Add Instance". This gives you a QR code. You scan it with your phone (just like WhatsApp Web). Now, WasenderAPI "owns" a connection to your WhatsApp number.

### Step 2: The "Listening" (Incoming Message)
When a customer sends a message to your phone:
1.  WhatsApp receives it.
2.  **WasenderAPI** "sees" it instantly.
3.  WasenderAPI needs to tell *your code* about it. But your code is hidden inside your local computer (localhost).

### Step 3: The "Tunnel" (localtunnel or ngrok)
This is where **localtunnel** comes in. It creates a public "tunnel" to your computer.
*   You run: `npx localtunnel --port 8000`
*   You get a public link like: `https://shorthand.loca.lt`

### Step 4: The WasenderAPI Settings (Crucial)
1.  **Log in** to your WasenderAPI Dashboard.
2.  Go to **Instances** and select your active device.
3.  Click the **Settings** (Gear icon).
4.  Find the **Webhook URL** field.
5.  **Paste** your tunnel link followed by our endpoint:
    `https://shorthand.loca.lt/webhook/whatsapp`
6.  Set **Webhook Status** to **Enabled**.
7.  **Save Settings**.

### Step 4: The "Webhook" Data Flow
Now, the chain is complete:
`User Phone` ➔ `WhatsApp Servers` ➔ `WasenderAPI` ➔ `ngrok Tunnel` ➔ `Your main.py (webhook endpoint)`

### Step 5: Evaluation & Verification (The Reply)
This step happens **automatically** inside the code. Here is how you "Evaluate" if the program is working:

#### A. How the code "Executes" the reply:
Inside `main.py`, as soon as Bob finishes thinking, the program calls the **WasenderAPI**. It tells Wasender: *"Hey, I have an answer for [User's Phone Number]. Please send this text back to them."*

#### B. How YOU evaluate the program:
You can verify the success in three places:

1.  **The Visual Test (Real World)**: 
    *   Pick up your phone. 
    *   If you receive a reply from "Bob" on WhatsApp, the whole chain is working!

2.  **The Terminal Test (The Code)**:
    *   Look at your `uvicorn` terminal. 
    *   You should see a line like: `INFO: 127.0.0.1 - "POST /webhook/whatsapp HTTP/1.1" 200 OK`.
    *   This means your code successfully received the message and finished processing it.

3.  **The Database Test (The Logs)**:
    *   Go to your **Supabase Dashboard** -> **Table Editor**.
    *   Open the `messages` table. 
    *   You should see a new row with the `role` as **assistant** and the `content` containing Bob's answer.

#### C. What if it fails?
*   If you get the message but no reply: Check your `WASENDER_API_KEY` in the `.env` file.
*   If you see no logs in the terminal: Check that your `localtunnel` URL in the WasenderAPI settings is correct and has `/webhook/whatsapp` at the end.

---

## 📊 4. Database Schema (Supabase)
*   **`documents`**: Keeps track of what you've uploaded.
*   **`conversations`**: Stores unique phone numbers so we know who is talking.
*   **`messages`**: Stores every single "User" and "Assistant" message for your logs.

---

## 🛠️ Key Files to Explore:
*   `main.py`: The "Brain" that handles all the web requests.
*   `services/doc_processor.py`: Handles PDFs and vectorizing text.
*   `services/rag_service.py`: Handles searching Pinecone for answers.
*   `services/llm_manager.py`: Handles the multi-AI fallback logic.
