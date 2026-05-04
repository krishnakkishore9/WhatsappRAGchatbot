# Deploying WhatsApp RAG Chatbot on Render

This document provides a step-by-step guide for deploying your chatbot to Render. Render is highly recommended for this project because it runs a persistent container, meaning it can easily handle the heavy Machine Learning dependencies (like `SentenceTransformer` and PyTorch) and background tasks without the timeouts that occur on serverless platforms like Vercel.

---

## Step-by-Step Deployment Guide

### 1. Preparation
Ensure your code is pushed to your GitHub repository. Your project must have:
* `main.py`
* `requirements.txt`
* All necessary Python files.

If you have made recent changes and need to push your code to GitHub, run these commands in your terminal:

```powershell
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Create a Render Account
Go to [Render.com](https://render.com) and sign up/log in using your GitHub account.

### 3. Create a New Web Service
1. In your Render Dashboard, click the **New +** button in the top right corner.
2. Select **Web Service**.
3. Connect your GitHub repository (`WhatsappRAGChatbot`).

### 4. Configure the Web Service
Fill in the deployment settings as follows:
* **Name**: `whatsapp-rag-chatbot` (or whatever you prefer)
* **Region**: Choose the region closest to you or your Pinecone database (e.g., US East).
* **Branch**: `main` (or your primary branch).
* **Runtime**: `Python 3`
* **Build Command**: `pip install -r requirements.txt`
* **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`

*(Note: Render will automatically detect the port if specified, but `10000` is Render's default.)*

### 5. Set Environment Variables
Scroll down to **Environment Variables** and click **Add Environment Variable**. Add all the variables exactly as they appear in your local `.env` file:

* `SUPABASE_URL` = `your_supabase_url`
* `SUPABASE_KEY` = `your_supabase_key`
* `OPENAI_API_KEY` = `your_openai_api_key`
* `PINECONE_API_KEY` = `your_pinecone_api_key`
* `WASENDER_API_KEY` = `your_wasender_api_key`
* `HF_API_KEY` = `your_huggingface_api_key` (if applicable)
* `GEMINI_API_KEY` = `your_gemini_api_key` (if applicable)

### 6. Deploy
1. Click **Create Web Service**.
2. Render will begin building your container. It will download PyTorch and your other dependencies. This first build may take 5-10 minutes because ML libraries are large.
3. Once deployed successfully, Render will provide a live URL near the top of the dashboard (e.g., `https://whatsapp-rag-chatbot.onrender.com`).

### 7. Update WasenderAPI Webhook
1. Copy your new Render URL.
2. Log in to your WasenderAPI dashboard.
3. Go to your instance **Settings**.
4. Update the Webhook URL to: `https://your-render-url.onrender.com/webhook/whatsapp`
5. Ensure the webhook is **Enabled** and save.

Your chatbot is now live and running in a persistent environment!
