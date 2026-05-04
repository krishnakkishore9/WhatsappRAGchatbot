# 🚀 Deployment Guide

This guide provides step-by-step instructions to take your project from local development to a live production environment.

---

## 🛠️ Prerequisites

- A [GitHub](https://github.com/) account.
- A [Vercel](https://vercel.com/) account.
- API keys for OpenAI, Pinecone, Supabase, and WasenderAPI.

---

## 📤 Step 1: Upload to GitHub

1. **Initialize Git**:
   Open your terminal in the project root and run:
   ```bash
   git init
   ```

2. **Add Files**:
   Create a `.gitignore` file to avoid uploading sensitive information:
   ```bash
   echo ".env" > .gitignore
   echo "__pycache__/" >> .gitignore
   echo "uploads/" >> .gitignore
   ```
   Then add and commit your files:
   ```bash
   git add .
   git commit -m "Initial commit: WhatsApp RAG Chatbot"
   ```

3. **Push to GitHub**:
   - Create a new repository on GitHub.
   - Run the following (replace `<URL>` with your repo URL):
   ```bash
   git remote add origin <URL>
   git branch -M main
   git push -u origin main
   ```

---

## 🌍 Step 2: Deploy to Vercel

1. **Import Project**:
   - Go to your [Vercel Dashboard](https://vercel.com/dashboard).
   - Click **Add New** > **Project**.
   - Select your GitHub repository.

2. **Configure Settings**:
   - **Framework Preset**: Select "Other" (Vercel will detect the `vercel.json`).
   - **Root Directory**: `./`

3. **Add Environment Variables**:
   In the **Environment Variables** section, add the following keys exactly as they appear in your `.env` file:
   - `OPENAI_API_KEY`
   - `PINECONE_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `WASENDER_API_KEY`
   - `HF_API_KEY`

4. **Deploy**:
   Click **Deploy**. Once finished, Vercel will provide you with a production URL (e.g., `https://my-chatbot.vercel.app`).

---

## 🔗 Step 3: Configure WhatsApp Webhook

1. **Get your URL**: Your live webhook URL will be `https://<your-vercel-domain>/webhook/whatsapp`.
2. **WasenderAPI Setup**:
   - Log in to your WasenderAPI dashboard.
   - Locate the **Webhook Settings** section.
   - Paste your Vercel webhook URL.
   - Save the settings.

---

## 🧪 Step 4: Final Verification

1. **Admin Panel**: Visit `https://<your-vercel-domain>/admin` to ensure the UI is loading.
2. **Test Upload**: Upload a small text file and wait for the status to change to `indexed`.
3. **WhatsApp Message**: Send a message to your connected WhatsApp number and check if the bot responds based on the uploaded file.
4. **Check Logs**: Verify the interaction appears in the "Recent Logs" section of your Admin Panel.
