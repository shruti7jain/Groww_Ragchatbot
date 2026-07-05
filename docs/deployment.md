# Deployment Guide: Railway & Vercel

This project uses a decoupled deployment strategy:
- **Backend (FastAPI & AI Models)**: Deployed on **Railway**
- **Frontend (Static UI)**: Deployed on **Vercel**

This guide will walk you through deploying both components from this GitHub repository.

---

## 1. Deploying the Backend on Railway

The backend handles the data ingestion, text embedding, FAISS vector search, and LLM generation. It needs to be deployed first so you have a URL for the frontend to connect to.

### Steps:
1. Go to [Railway.app](https://railway.app/) and log in.
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select this repository (`Groww_Ragchatbot`).
4. Railway will automatically detect the Python environment and read the `railway.json` file we created, which tells it to start the server using Uvicorn.
5. **Add Environment Variables**:
   - Go to your Railway project dashboard and click on the newly created service.
   - Go to the **Variables** tab.
   - Add all the variables from your local `.env` file:
     - `GEMINI_API_KEY`
     - `GROQ_API_KEY`
     - `LLM_PROVIDER` (e.g., `gemini`)
     - `TOP_K_RETRIEVAL` (e.g., `3`)
     - `SIMILARITY_THRESHOLD` (e.g., `0.5`)
     - `VECTOR_STORE_TYPE` (e.g., `faiss`)
     - `EMBEDDING_MODEL` (e.g., `BAAI/bge-base-en-v1.5`)
6. **Generate a Public URL**:
   - Go to the **Settings** tab of your service.
   - Under the **Networking** section, click **Generate Domain**.
   - Copy this URL (e.g., `https://your-project.up.railway.app`). You will need it for the Vercel deployment.

---

## 2. Deploying the Frontend on Vercel

The frontend is a lightweight, static HTML/JS file. To avoid Cross-Origin (CORS) issues and make deployment seamless, we use a `vercel.json` configuration file that proxies API requests to your Railway backend.

### Steps:
1. **Update `vercel.json`**:
   - In your local project repository, open `vercel.json`.
   - On line 6, you will see `"destination": "https://<YOUR-RAILWAY-APP-URL>.up.railway.app/api/$1"`.
   - Replace the `https://...` URL with the public domain you generated in Railway in step 1.6.
   - Commit and push this change to your GitHub repository.
2. Go to [Vercel.com](https://vercel.com/) and log in.
3. Click **Add New...** -> **Project**.
4. Import this GitHub repository (`Groww_Ragchatbot`).
5. In the **Configure Project** screen:
   - **Framework Preset**: Leave it as **Other**.
   - **Root Directory**: Leave it as `./`.
   - **Environment Variables**: Leave this completely blank! Vercel only serves the static HTML; it does not need your API keys.
6. Click **Deploy**.

Vercel will automatically read the `vercel.json` file. It will serve your `index.html` file from the `src/app/static` directory and intelligently route any `/api/chat` requests to your Railway backend!

### Troubleshooting
- **Chat is stuck on "Thinking..."**: Check your Railway logs. Make sure you entered the correct Environment Variables in Railway and that your API keys are valid.
- **Network / 404 Errors**: Double-check that the `destination` URL in your `vercel.json` exactly matches your Railway public domain.
