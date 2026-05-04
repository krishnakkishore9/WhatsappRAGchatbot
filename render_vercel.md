# Deploying WhatsApp RAG Chatbot on Render

This document explains why the application should be deployed on Render instead of Vercel, and provides a step-by-step guide for deploying it to Render.

## Why Render instead of Vercel?

When deploying an AI/RAG application that uses local Machine Learning models, Vercel is often not the right fit due to the limitations of Serverless Functions:

1. **Heavy ML Dependencies**: This project uses `SentenceTransformer('all-MiniLM-L6-v2')` which relies on PyTorch. PyTorch is a massive library (>800MB) that exceeds Vercel's 250MB unzipped size limit for serverless functions.
2. **Cold Start Timeouts**: Vercel's free tier has a strict 10-second timeout for serverless functions. Loading PyTorch and downloading the model weights takes much longer than 10 seconds, leading to immediate `500: INTERNAL_SERVER_ERROR (FUNCTION_INVOCATION_FAILED)` crashes on startup.
3. **Background Tasks**: The application uses FastAPI's `BackgroundTasks` to process WhatsApp messages without keeping the webhook waiting. Vercel freezes the execution environment the moment an HTTP response is returned, which breaks background tasks and prevents the bot from answering.

Render uses persistent containers, meaning the application stays running, can load heavy ML models comfortably, and can process background tasks without interruption.

## Step-by-Step Deployment Guide for Render

### 1. Preparation
Ensure your code is pushed to a GitHub repository. Your project must have:
* `main.py`
* `requirements.txt`
* All necessary Python files.

### 2. Create a Render Account
Go to [Render.com](https://render.com) and sign up/log in using your GitHub account.

### 3. Create a New Web Service
1. Click the **New +** button in the top right corner.
2. Select **Web Service**.
3. Connect your GitHub repository containing the WhatsApp RAG Chatbot.

### 4. Configure the Web Service
Fill in the deployment settings as follows:
* **Name**: `whatsapp-rag-chatbot` (or whatever you prefer)
* **Region**: Choose the region closest to you or your Pinecone database (e.g., US East).
* **Branch**: `main` (or your primary branch).
* **Runtime**: `Python 3`
* **Build Command**: `pip install -r requirements.txt`
* **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`

*Note: Render will automatically detect the port if specified, but `10000` is Render's default.*

### 5. Set Environment Variables
Vercel's failure is often partly due to missing environment variables. Render needs these to function. 
Scroll down to **Environment Variables** and click **Add Environment Variable**. Add all the variables from your local `.env` file:

* `SUPABASE_URL` = `your_supabase_url`
* `SUPABASE_KEY` = `your_supabase_key`
* `OPENAI_API_KEY` = `your_openai_api_key`
* `PINECONE_API_KEY` = `your_pinecone_api_key`
* `WASENDER_API_KEY` = `your_wasender_api_key`
* `HF_API_KEY` = `your_huggingface_api_key` (if applicable)
* `GEMINI_API_KEY` = `your_gemini_api_key` (if applicable)

### 6. Deploy
1. Click **Create Web Service**.
2. Render will begin building your container. It will download PyTorch and your other dependencies. This first build may take 5-10 minutes.
3. Once deployed, Render will provide a live URL (e.g., `https://whatsapp-rag-chatbot.onrender.com`).

### 7. Update WasenderAPI Webhook
1. Copy your new Render URL.
2. Log in to your WasenderAPI dashboard.
3. Go to your instance **Settings**.
4. Update the Webhook URL to: `https://your-render-url.onrender.com/webhook/whatsapp`
5. Ensure the webhook is **Enabled** and save.

Your chatbot is now live and running in a persistent environment!
