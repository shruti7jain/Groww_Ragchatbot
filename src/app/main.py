"""
FastAPI application for the Groww Mutual Fund FAQ RAG Chatbot.
Serves the UI and the /api/chat endpoint.
"""
import os
import sys
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Ensure project root is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.generation.response_builder import ResponseBuilder

# --- Lifespan: load heavy models once on startup ---
builder: ResponseBuilder = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global builder
    logging.info("Loading RAG pipeline (FAISS index + BGE model)...")
    builder = ResponseBuilder()
    logging.info("RAG pipeline ready.")
    yield
    logging.info("Shutting down.")

app = FastAPI(title="Groww MF FAQ Assistant API", lifespan=lifespan)

# --- Static files & HTML ---
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open(os.path.join(static_dir, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

# --- Chat endpoint ---
class ChatRequest(BaseModel):
    query: str

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        result = builder.answer(request.query)
        return {
            "response":     result.get("response", ""),
            "sources":      result.get("sources", []),
        }
    except Exception as e:
        return {
            "response":     f"Server error: {str(e)}",
            "sources":      [],
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app.main:app", host="127.0.0.1", port=8000, reload=False)
