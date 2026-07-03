# Groww Mutual Fund FAQ RAG Chatbot

> **Facts-only. No investment advice.**

## Project Overview
A custom Retrieval-Augmented Generation (RAG) chatbot designed to answer factual questions about mutual fund schemes listed on Groww. It intercepts and refuses advisory queries to ensure compliance with facts-only requirements.

---

## Disclaimer

This tool provides publicly available, factual information only (expense ratios, exit loads, riskometer ratings, SIP amounts, etc.).  
It **does not** provide investment advice, fund comparisons, return predictions, or personal recommendations.

---

## Corpus

The application corpus contains 20 specific Groww mutual fund scheme pages:
- **10 Union Mutual Funds**
- **10 HDFC Mutual Funds**

*Source: Only the 20 Groww URLs provided — no PDFs, no AMC websites, no other external sources.*

---

## Architecture

**Pipeline overview:**
```
Offline:  Scraper → Chunker → BGE Embedder → FAISS Index
Online:   User Query → Classifier → Retriever → LLM → Response + Citation
```

---

## Prerequisites

- **Python 3.10+**
- **API Keys** (both free):
  - Gemini API key → [aistudio.google.com](https://aistudio.google.com)
  - Groq API key   → [console.groq.com](https://console.groq.com)

---

## Setup and Installation

```bash
# 1. Clone the repository
git clone <repo-url>
cd Groww_RagChatBot

# 2. Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Open .env and fill in GEMINI_API_KEY and GROQ_API_KEY
```

---

## How to Switch LLM Providers

You can switch the language model provider seamlessly between Groq (Llama3) and Google Gemini by editing the `.env` file.

1. Open `.env`
2. Change the `LLM_PROVIDER` key:
   - For Groq: `LLM_PROVIDER=groq`
   - For Gemini: `LLM_PROVIDER=gemini`
3. Restart the FastAPI server for changes to take effect.

---

## Running the Application

### 1. Build the Index (Offline — Run Once)

```bash
python scripts/build_index.py
```

This runs the full offline pipeline:
1. Scrapes all 20 Groww fund pages (`src/scraper/scraper.py`)
2. Converts records to text chunks (`src/ingestion/chunker.py`)
3. Generates embeddings using `BAAI/bge-small-en-v1.5` (384-dim)
4. Builds and saves the FAISS vector index (`src/ingestion/indexer.py`)

Output: `data/vector_store/index.faiss` + `data/vector_store/metadata.pkl`

### 2. Start the UI Server

```bash
python -m src.app.main
```

Open [http://localhost:8000](http://localhost:8000) in your browser to interact with the chatbot interface.

---

## Known Limitations

| Limitation | Detail |
|---|---|
| Static corpus | Data is scraped once; re-indexing required for updates |
| No live NAV | Only the NAV present at scrape time is stored |
| 20 schemes only | Only the 20 selected schemes are in scope |
| English only | No multilingual support |
| Groww URLs only | No PDFs, no AMC sites, no other external sources |

---

## Project Structure

```
Groww_RagChatBot/
├── docs/                   # Architecture, implementation plan, eval guides
├── data/                   # Scraped data, chunks, vector store (not committed)
├── src/
│   ├── scraper/            # Groww page scraper + URL registry
│   ├── ingestion/          # Chunker, embedder, FAISS indexer
│   ├── retrieval/          # Query classifier + retriever
│   ├── generation/         # LLM client, prompt templates, response builder
│   └── app/                # FastAPI backend + Static HTML/JS/CSS UI
├── scripts/                # One-shot build + validation scripts
├── tests/                  # Unit and E2E tests
├── requirements.txt
├── .env.example
└── README.md
```
