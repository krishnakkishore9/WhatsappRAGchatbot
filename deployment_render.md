# Deploying WhatsApp RAG Chatbot on Render

This document provides a step-by-step guide for deploying your chatbot to Render. Render is recommended for this project because it runs a **persistent container**, handling background tasks and network calls without the timeouts that occur on serverless platforms like Vercel.

> **Live URL**: `https://whatsappragchatbot.onrender.com`
> **Webhook URL**: `https://whatsappragchatbot.onrender.com/webhook/whatsapp`
> **Admin UI**: `https://whatsappragchatbot.onrender.com/admin`

---

## ✅ Working Environment (Confirmed)

| Component | Details |
|---|---|
| **Platform** | Render (Free Web Service) |
| **Python Version** | 3.11.9 (pinned via `.python-version`) |
| **Embeddings** | FastEmbed — `BAAI/bge-small-en-v1.5` via ONNX (384 dims, no PyTorch) |
| **LLM** | Google Gemini (via `llm_manager.py` with fallback chain) |
| **Vector DB** | Pinecone — index: `txstate-rag-v2` (384 dimensions, cosine) |
| **Database** | Supabase (conversations, messages, documents tables) |
| **WhatsApp Bridge** | WasenderAPI |

---

## 🚀 Step-by-Step Deployment Guide

### 1. Preparation — Push Code to GitHub

Ensure all your code is pushed to GitHub before deploying:

```powershell
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

Your repository must contain:
- `main.py`
- `requirements.txt`
- `services/` folder (all `.py` files)
- `static/index.html`
- `.python-version` (pins Python 3.11.9)

### 2. Create a Render Account
Go to [Render.com](https://render.com) and sign up/log in using your GitHub account.

### 3. Create a New Web Service
1. In your Render Dashboard, click **New +** → **Web Service**.
2. Connect your GitHub repository (`WhatsappRAGChatbot`).

### 4. Configure the Web Service
Fill in the deployment settings as follows:

| Setting | Value |
|---|---|
| **Name** | `whatsappragchatbot` |
| **Region** | Oregon (US West) or closest to you |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Python Version** | `3.11.9` ← Set this in Render Settings |
| **Build Command** | `pip install --no-cache-dir -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port 10000` |

> ⚠️ **Important**: Set Python version to **3.11.9** in Render's Settings panel. The `fastembed` library has Rust dependencies that are incompatible with Python 3.14 (Render's default).

### 5. Set Environment Variables
Go to **Environment** and add all the following variables:

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Your Supabase service role key |
| `OPENAI_API_KEY` | OpenAI key (used as LLM fallback) |
| `PINECONE_API_KEY` | Pinecone API key |
| `WASENDER_API_KEY` | WasenderAPI key for sending replies |
| `HF_API_KEY` | HuggingFace API key |
| `GEMINI_API_KEY` | Google Gemini API key (primary LLM) |

### 6. Deploy
1. Click **Create Web Service**.
2. First build takes **5–10 minutes** (downloads FastEmbed ONNX model ~90MB).
3. Once deployed, you'll see your live URL at the top of the dashboard.

### 7. Upload Your Documents
1. Go to `https://<your-render-url>/admin`
2. Upload all your PDFs one by one.
3. Wait for each to show **"indexed"** status before testing.

### 8. Configure WasenderAPI Webhook
1. Log in to your WasenderAPI dashboard.
2. Go to your instance → **Settings**.
3. Set Webhook URL to:
   ```
   https://whatsappragchatbot.onrender.com/webhook/whatsapp
   ```
4. Set **Webhook Status** to **Enabled** and save.

> **Note**: For real WhatsApp messages, no Personal Access Token is needed. The WasenderAPI "Simulate" button requires a PAT — just send a real WhatsApp message to test instead.

---

## 🔄 Redeploying After Code Changes

```powershell
# Make your changes, then:
git add .
git commit -m "Your change description"
git push origin main
# Then in Render: Manual Deploy → Deploy latest commit
```

> Use **"Clear build cache & deploy"** only when changing Python version or dependencies.

---

## ⚠️ Free Tier Limitations

- **Cold starts**: The free instance spins down after **15 minutes of inactivity**. The first message after idle time may take **50+ seconds** to respond.
- **Memory**: 512MB RAM limit. FastEmbed (ONNX) uses ~150MB — well within limits.
- **Disk**: Ephemeral filesystem. The `uploads/` folder is recreated on every deploy — uploaded PDFs are re-indexed into Pinecone but the files themselves are temporary.

---

## 🩺 Health Check & Debug Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /health` | Check server and Supabase status |
| `GET /admin/debug` | Verify all environment variables are set |
| `GET /admin/documents` | List all indexed documents |
| `GET /admin/logs` | View recent chat messages |
