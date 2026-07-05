# Architecture: Groww Mutual Fund FAQ RAG Chatbot

> **Version**: 1.0.0 | **Last Updated**: 2026-06-30 | **AMCs in Scope**: Union Mutual Fund, HDFC Mutual Fund

---

## Table of Contents

1. [High-Level Overview](#1-high-level-overview)
2. [Component Architecture](#2-component-architecture)
3. [Phase 1: Data Ingestion Pipeline](#3-phase-1-data-ingestion-pipeline)
4. [Phase 2: Indexing & Vector Store](#4-phase-2-indexing--vector-store)
5. [Phase 3: Query Processing Pipeline](#5-phase-3-query-processing-pipeline)
6. [Phase 4: Response Generation](#6-phase-4-response-generation)
7. [Phase 5: User Interface Layer](#7-phase-5-user-interface-layer)
8. [Phase 6: Scheduled Data Maintenance](#8-phase-6-scheduled-data-maintenance)
9. [Directory Structure](#9-directory-structure)
9. [Technology Stack](#9-technology-stack)
10. [Data Flow Diagram](#10-data-flow-diagram)
11. [Component Interaction Sequence](#11-component-interaction-sequence)
12. [Scraper Design](#12-scraper-design)
13. [Vector Store Design](#13-vector-store-design)
14. [Query Classifier Design](#14-query-classifier-design)
15. [LLM Prompt Design](#15-llm-prompt-design)
16. [Privacy & Security Architecture](#16-privacy--security-architecture)
17. [Error Handling Strategy](#17-error-handling-strategy)
18. [Known Limitations](#18-known-limitations)

---

## 1. High-Level Overview

The system is a **Retrieval-Augmented Generation (RAG)** chatbot that answers factual queries about mutual fund schemes from two AMCs: **Union Mutual Fund** and **HDFC Mutual Fund**.

It operates in two distinct phases:

```
┌─────────────────────────────────────────────────────────────────────┐
│                     OFFLINE / BUILD-TIME PHASE                      │
│                                                                     │
│   Scraper → Raw Text Chunks → Embeddings → Vector Store (Index)     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      ONLINE / RUNTIME PHASE                         │
│                                                                     │
│   User Query → Classifier → Retriever → LLM → Response + Citation  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      MAINTENANCE PHASE                              │
│                                                                     │
│   Scheduler ──(Triggers Daily)──▶ Offline / Build-time Phase        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          GROWW RAG CHATBOT SYSTEM                        │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                   INGESTION PIPELINE (Offline)                   │    │
│  │                                                                  │    │
│  │  ┌────────────┐   ┌─────────────┐    ┌──────────────┐            │    │
│  │  │ Scheduler  │──▶│   Scraper   │───▶│ Text Chunker │            │    │
│  │  │ (Daily Job)│   │  (Groww +   │    │  (LangChain  │            │    │
│  │  └────────────┘   │  AMC pages) │    │  splitter)   │            │    │
│  │                   └─────────────┘    └──────────────┘            │    │
│  │                                            │                     │    │
│  │                                            ▼                     │    │
│  │                                   ┌────────────────────┐         │    │
│  │                                   │  Embedding Model   │         │    │
│  │                                   │ (sentence-         │         │    │
│  │                                   │  transformers)     │         │    │
│  │                                   └────────┬───────────┘         │    │
│  │                                            │                     │    │
│  │                                            ▼                     │    │
│  │                                   ┌────────────────┐             │    │
│  │                                   │  Vector Store  │             │    │
│  │                                   │ (FAISS/Chroma) │             │    │
│  │                                   └────────────────┘             │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                     RUNTIME PIPELINE (Online)                    │    │
│  │                                                                  │    │
│  │  ┌──────┐  ┌──────────────┐  ┌───────────┐  ┌───────────────┐  │    │
│  │  │  UI  │─▶│  Query       │─▶│ Retriever │─▶│  LLM Layer    │  │    │
│  │  │      │  │  Classifier  │  │           │  │  (Generator)  │  │    │
│  │  │      │◀─│              │  │           │  │               │  │    │
│  │  └──────┘  └──────────────┘  └───────────┘  └───────────────┘  │    │
│  │   (chat)   (factual/refuse)  (top-k chunks)  (≤3 sentences +   │    │
│  │                                               citation)         │    │
│  └──────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Phase 1: Data Ingestion Pipeline

### 3.1 Overview

The ingestion pipeline runs **once offline** (or periodically re-indexed) and produces the vector store that powers retrieval at runtime.

```
URL List (20 Groww links)
        │
        ▼
   ┌──────────┐
   │ Scraper  │  ←── Single generic scraper handles all 20 URLs
   │ (Python) │       (same Groww page layout for all funds)
   └────┬─────┘
        │ Raw HTML / Text per fund
        ▼
   ┌────────────────┐
   │ Text Extractor │  ←── BeautifulSoup / Playwright
   │                │       extracts: fund name, expense ratio,
   │                │       exit load, riskometer, benchmark,
   │                │       min SIP, fund category, NAV
   └────┬───────────┘
        │ Structured text per fund
        ▼
   ┌────────────────┐
   │ Text Chunker   │  ←── LangChain RecursiveCharacterTextSplitter
   │                │       chunk_size=500, overlap=50
   └────┬───────────┘
        │ List of (chunk_text, source_url, fund_name, amc_name, scraped_date)
        ▼
   ┌─────────────────┐
   │ Embedding Model │  ←── BAAI/bge-base-en-v1.5 (768-dim)
   │                 │       (runs locally via sentence-transformers, no API cost)
   └────┬────────────┘
        │ Dense vectors (768-dim)
        ▼
   ┌────────────────┐
   │  Vector Store  │  ←── FAISS (local) or ChromaDB (persistent)
   │  + Metadata    │       stores: vector + chunk_text + source_url
   └────────────────┘
```

### 3.2 Corpus URLs Ingested

**Union Mutual Fund (10 schemes):**

| # | Fund Name | Source URL |
|---|---|---|
| 1 | Union Small Cap Fund | https://groww.in/mutual-funds/union-small-and-midcap-fund-direct-growth |
| 2 | Union Liquid Fund | https://groww.in/mutual-funds/union-liquid-fund-direct-growth |
| 3 | Union Midcap Fund | https://groww.in/mutual-funds/union-midcap-fund-direct-growth |
| 4 | Union Flexi Cap Fund | https://groww.in/mutual-funds/union-equity-fund-direct-growth |
| 5 | Union Active Momentum Fund | https://groww.in/mutual-funds/union-active-momentum-fund-direct-growth |
| 6 | Union Children's Fund | https://groww.in/mutual-funds/union-childrens-fund-direct-growth |
| 7 | Union Multi Asset Allocation Fund | https://groww.in/mutual-funds/union-multi-asset-allocation-fund-direct-growth |
| 8 | Union Multicap Fund | https://groww.in/mutual-funds/union-multicap-fund-direct-growth |
| 9 | Union Gold ETF FoF | https://groww.in/mutual-funds/union-gold-etf-fof-direct-growth |
| 10 | Union Innovation & Opportunities Fund | https://groww.in/mutual-funds/union-innovation-opportunities-fund-direct-growth |

**HDFC Mutual Fund (10 schemes):**

| # | Fund Name | Source URL |
|---|---|---|
| 1 | HDFC Silver ETF FoF | https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth |
| 2 | HDFC Mid Cap Fund | https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth |
| 3 | HDFC Flexi Cap Fund | https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth |
| 4 | HDFC Defence Fund | https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth |
| 5 | HDFC Small Cap Fund | https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth |
| 6 | HDFC Gold ETF Fund of Fund | https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth |
| 7 | HDFC Short Term Debt Fund | https://groww.in/mutual-funds/hdfc-short-term-opportunities-fund-direct-growth |
| 8 | HDFC Balanced Advantage Fund | https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth |
| 9 | HDFC NIFTY 50 Index Fund | https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth |
| 10 | HDFC Pharma And Healthcare Fund | https://groww.in/mutual-funds/hdfc-pharma-and-healthcare-fund-direct-growth |

> **Note**: A single generic scraper handles all 20 URLs — both AMCs use the same Groww page layout and HTML structure, so no separate scraper is needed per AMC.

### 3.3 Fields Extracted Per Scheme

```python
{
  "fund_name":       "HDFC Mid Cap Fund",
  "amc":             "HDFC Mutual Fund",
  "category":        "Mid Cap",
  "nav":             "₹XXX.XX",
  "expense_ratio":   "X.XX%",
  "exit_load":       "1% if redeemed within 1 year",
  "min_sip":         "₹100",
  "riskometer":      "Very High",
  "benchmark":       "NIFTY Midcap 150 TRI",
  "lock_in":         "N/A",          # or "3 years" for ELSS
  "source_url":      "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
  "scraped_date":    "30-Jun-2026"
}
```

---

## 4. Phase 2: Indexing & Vector Store

### 4.1 Chunking Strategy

```
Raw page text
    │
    ├── Split by field boundaries (structured extraction)
    │       Each field (expense ratio, exit load, etc.) = 1 chunk
    │
    └── Fallback: RecursiveCharacterTextSplitter
            chunk_size  = 500 characters
            chunk_overlap = 50 characters
```

### 4.2 Chunk Metadata Schema

Each stored chunk carries metadata alongside its vector:

```python
{
  "chunk_id":     "union_midcap_chunk_3",
  "text":         "The expense ratio of Union Midcap Fund (Direct Plan) is X.XX% as of Jun 2026.",
  "source_url":   "https://groww.in/mutual-funds/union-midcap-fund-direct-growth",
  "fund_name":    "Union Midcap Fund",
  "amc":          "Union Mutual Fund",
  "field":        "expense_ratio",
  "scraped_date": "30-Jun-2026"
}
```

### 4.3 Embedding Model

| Property | Value |
|---|---|
| **Model** | `BAAI/bge-base-en-v1.5` |
| **Dimensions** | **768** |
| **Runs** | Locally via `sentence-transformers` (no API key required) |
| **MTEB Retrieval Rank** | Top-5 for English retrieval tasks |
| **Query Prefix** | Required: `"Represent this sentence for searching relevant passages: "` |
| **Similarity** | Cosine similarity (inner product on L2-normalised vectors) |
| **Library** | `sentence-transformers` + `FlagEmbedding` (Python) |
| **License** | MIT — fully free |

> **Why BGE over MiniLM?** `BAAI/bge-base-en-v1.5` consistently outperforms `all-MiniLM-L6-v2` on the MTEB retrieval benchmark, produces richer 768-dim representations, and is still fast on CPU. The only extra requirement is a query instruction prefix at runtime.

### 4.4 Vector Store Options

| Option | When to Use | Pros | Cons |
|---|---|---|---|
| **FAISS** (default) | Local / lightweight dev | Fast, no server needed, free | Not persistent across restarts without save/load |
| **ChromaDB** | Persistent / production | Persistent on disk, metadata filtering | Slightly heavier setup |

---

## 5. Phase 3: Query Processing Pipeline

### 5.1 Runtime Query Flow

```
User types query
       │
       ▼
┌──────────────────────────────┐
│     Query Classifier         │
│                              │
│  Is the query factual?       │
│  ┌──────────┬───────────┐   │
│  │  YES     │    NO     │   │
│  └────┬─────┴─────┬─────┘   │
└───────│───────────│─────────┘
        │           │
        ▼           ▼
  Proceed to    Return polite
  Retrieval     REFUSAL response
                + AMFI/SEBI link
        │
        ▼
┌──────────────────────────────┐
│       Retriever              │
│                              │
│  1. Embed user query         │
│  2. Similarity search in     │
│     vector store (top-k=3)   │
│  3. Return chunks + metadata │
└──────────┬───────────────────┘
           │ (chunk_text, source_url, scraped_date)
           ▼
┌──────────────────────────────┐
│     LLM Response Generator  │
│                              │
│  Input: query + retrieved   │
│         chunks + prompt     │
│  Output: ≤3 sentence answer │
│         + 1 citation URL    │
│         + last updated date │
└───────────┬──────────────────┘
```

### 5.2 Retrieval Parameters

| Parameter | Value | Rationale |
|---|---|---|
| **top-k chunks** | 3 | Provides enough context without noise |
| **Similarity threshold** | 0.5 (cosine) | Prevents hallucination from irrelevant results |
| **Re-ranking** | Optional (cross-encoder) | Improves precision for ambiguous queries |

---

## 6. Phase 4: Response Generation

### 6.1 LLM Options

All LLM options used are **free** — no paid API required.

| Option | Model | Provider | Cost |
|---|---|---|---|
| **Primary** | `gemini-1.5-flash` | Google AI Studio API | ✅ Free tier (aistudio.google.com) |
| **Fallback** | `llama3-8b-8192` | Groq API | ✅ Free tier (console.groq.com) |
| **Local (optional)** | `mistral-7b-instruct` | Ollama | ✅ Free, needs GPU/RAM |

### 6.2 Response Format Contract

Every generated response **must** conform to:

```
[Factual answer in ≤ 3 sentences. No opinions. No comparisons.]

Source: [Exactly one URL from the retrieved chunk metadata]

Last updated from sources: [DD-MMM-YYYY from chunk scraped_date]
```

**Example:**

```
The expense ratio of HDFC Mid Cap Fund (Direct Plan) is 0.81% per annum.
This fee is deducted from the fund's Net Asset Value on a daily basis.
The riskometer classification for this fund is Very High.

Source: https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth

Last updated from sources: 30-Jun-2026
```

### 6.3 Refusal Response Format

```
I'm designed to answer facts-only questions about mutual fund schemes —
such as expense ratios, exit loads, SIP amounts, and riskometer ratings.
I cannot provide investment advice, fund comparisons, or return predictions.

Please ask a factual question about one of the Union MF or HDFC MF schemes available on Groww.

Facts-only. No investment advice.
```

---

## 7. Phase 5: User Interface Layer

### 7.1 UI Components

```
┌─────────────────────────────────────────────────────────┐
│  HEADER                                                 │
│  Groww Mutual Fund FAQ Assistant                        │
│  ⚠️  Facts-only. No investment advice.  [sticky banner] │
├─────────────────────────────────────────────────────────┤
│  WELCOME CARD                                           │
│  "Hi! I can answer factual questions about Union MF     │
│   and HDFC MF schemes listed on Groww."                 │
│                                                         │
│  Try asking:                                            │
│   • "What is the expense ratio of HDFC Mid Cap Fund?"   │
│   • "What is the exit load for Union Flexi Cap Fund?"   │
│   • "What is the minimum SIP for HDFC Small Cap Fund?"  │
├─────────────────────────────────────────────────────────┤
│  CHAT AREA                                              │
│  ┌──────────────────────────────────────────────────┐   │
│  │ [User message]                                   │   │
│  │ [Assistant response + source citation]           │   │
│  │ [Last updated from sources: DD-MMM-YYYY]         │   │
│  └──────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  INPUT BAR                                              │
│  [Type your question here...]           [Send →]        │
└─────────────────────────────────────────────────────────┘
```

### 7.2 UI Tech Options

| Option | Stack | When to Use |
|---|---|---|
| **Google Stitch** | Web | Desktop-only premium UI, rapid generation |
| **Gradio** | Python-native | Good for ML demos |
| **Flask + HTML/CSS** | Lightweight web | More customization |
| **React / Next.js** | Full web app | Production-grade UI |

### 7.3 Deployment Architecture

The application adopts a unified deployment strategy:
- **Full Stack**: Deployed on **Railway** via Nixpacks. The FastAPI application serves the `/api/chat` endpoint and also statically serves the frontend `index.html` file at the root route (`/`).

## 8. Phase 6: Scheduled Data Maintenance

### 8.1 Overview
Since Mutual Fund NAVs (Net Asset Values) and other properties like AUM can change frequently, the vector store must be kept up-to-date. The Scheduler Component handles this by triggering the offline Data Ingestion Pipeline periodically using GitHub Actions (e.g., daily at 2:00 AM).

### 8.2 Execution Flow
1. **Trigger**: A GitHub Actions workflow (`.github/workflows/schedule_ingestion.yml`) triggers based on a CRON expression.
2. **Execute Ingestion**: The runner spins up, installs dependencies, and executes `build_index.py`.
3. **Persist Data**: Once the new FAISS index and metadata pickle file are generated, the workflow can either commit the new artifacts back to the repository or trigger a remote deployment so the live application can pull the latest data.
4. **Logging & Alerts**: Success or failure is logged in the GitHub Actions console. If scraping fails, the workflow alerts the maintainer and the previous vector store remains intact.

---

## 9. Directory Structure

```
Groww_RagChatBot/
│
├── docs/
│   ├── problemstatement.txt       # Original problem statement
│   ├── context.md                 # Project context & requirements
│   └── architecture.md            # This file
│
├── data/
│   ├── raw/                       # Raw scraped HTML/text per fund
│   │   ├── union/
│   │   └── hdfc/
│   ├── chunks/                    # Processed text chunks (JSON)
│   └── vector_store/              # Persisted FAISS / ChromaDB index
│
├── src/
│   ├── scraper/
│   │   ├── scraper.py             # Generic Groww page scraper (handles both AMCs)
│   │   └── urls.py                # All 20 corpus URLs defined here
│   │
│   ├── ingestion/
│   │   ├── chunker.py             # Text splitting logic
│   │   ├── embedder.py            # Embedding model wrapper
│   │   └── indexer.py             # Builds & saves the vector store
│   │
│   ├── retrieval/
│   │   ├── retriever.py           # Query embedding + similarity search
│   │   └── classifier.py          # Factual vs advisory query classifier
│   │
│   ├── generation/
│   │   ├── llm.py                 # LLM wrapper (Gemini / Mistral / GPT)
│   │   ├── prompt_templates.py    # System + user prompt templates
│   │   └── response_builder.py   # Formats final response with citation
│   │
│   └── app/
│       ├── main.py                # Entry point
│       └── ui.py                  # Streamlit / Gradio UI
│
├── scripts/
│   └── build_index.py             # One-shot script: scrape → chunk → embed → index
│
├── requirements.txt
├── .env.example                   # LLM API keys template
└── README.md
```

---

## 9. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.10+ | Core implementation language |
| **Scraping** | `requests` + `BeautifulSoup4` / `Playwright` | Fetching & parsing Groww pages |
| **Text Splitting** | `langchain.text_splitter` | Chunking raw text |
| **Embedding Model** | `BAAI/bge-base-en-v1.5` (768-dim) | Generating dense vectors locally (free) |
| **Vector Store** | `FAISS` (768-dim) or `ChromaDB` | Storing & querying embeddings |
| **LLM (Primary)** | Gemini 1.5 Flash | Response generation (free tier) |
| **LLM (Fallback)** | Groq `llama3-8b-8192` | Response generation (free tier, ultra-fast) |
| **RAG Orchestration** | `LangChain` or custom pipeline | Connecting retrieval → generation |
| **UI** | `Streamlit` | Chat interface |
| **Environment** | `python-dotenv` | API key management |
| **Dependency Mgmt** | `pip` + `requirements.txt` | Package management |

---

## 10. Data Flow Diagram

```
                         ┌─────────────────────┐
                         │   20 Groww URLs      │
                         │ (10 Union + 10 HDFC) │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  scraper.py          │
                         │  (single scraper,    │
                         │  both AMCs)          │
                         └──────────┬──────────┘
                                    │ raw text + structured fields
                                    ▼
                         ┌─────────────────────┐
                         │  chunker.py          │
                         │  500-char chunks,    │
                         │  50-char overlap     │
                         └──────────┬──────────┘
                                    │ (chunk, metadata)
                                    ▼
                         ┌─────────────────────┐
                         │  embedder.py         │
                         │  BAAI/bge-base-en-v1.5│
                         │  → 768-dim vectors   │
                         └──────────┬──────────┘
                                    │ vectors
                                    ▼
                    ┌──────────────────────────────┐
                    │       Vector Store            │
                    │     FAISS / ChromaDB         │
                    │  {vector, chunk, source_url}  │
                    └──────────────┬───────────────┘
                                   │
          ┌────────────────────────┤ (at query time)
          │                        │
          ▼                        ▼
   User Query              Embed query → search
          │                top-k=3 chunks
          │                        │
          ▼                        ▼
   Query Classifier    Retrieved chunks + URLs
          │                        │
    ┌─────┴──────┐                 │
    │  Factual?  │                 │
    └─────┬──────┘                 │
     YES  │   NO──▶ Refusal msg    │
          │                        │
          └────────────────────────┘
                        │
                        ▼
               LLM (Gemini/Mistral)
                        │
                        ▼
          ┌─────────────────────────┐
          │  Final Response         │
          │  [Answer ≤ 3 sentences] │
          │  Source: [URL]          │
          │  Last updated: [date]   │
          └─────────────────────────┘
                        │
                        ▼
                  Streamlit UI
```

---

## 11. Component Interaction Sequence

```
User         UI           Classifier     Retriever       LLM
 │            │                │              │            │
 │──query────▶│                │              │            │
 │            │───classify────▶│              │            │
 │            │                │              │            │
 │            │  ┌─advisory?   │              │            │
 │            │◀─┤ return refusal              │            │
 │            │  └─factual?    │              │            │
 │            │                │──embed+search▶│            │
 │            │                │              │◀─top-k─────│
 │            │                │◀─chunks+URLs─│            │
 │            │                │──────────────────────────▶│
 │            │                │              │  generate  │
 │            │◀────────────────────────────────response───│
 │◀─response──│                │              │            │
```

---

## 12. Scraper Design

### 12.1 Why One Scraper for Both AMCs

Both Union MF and HDFC MF fund pages are on `groww.in` and share the **identical HTML structure**. A single scraper with a list of 20 URLs handles both AMCs:

```python
# src/scraper/urls.py

CORPUS_URLS = {
    "Union Mutual Fund": [
        "https://groww.in/mutual-funds/union-small-and-midcap-fund-direct-growth",
        "https://groww.in/mutual-funds/union-liquid-fund-direct-growth",
        "https://groww.in/mutual-funds/union-midcap-fund-direct-growth",
        "https://groww.in/mutual-funds/union-equity-fund-direct-growth",
        "https://groww.in/mutual-funds/union-active-momentum-fund-direct-growth",
        "https://groww.in/mutual-funds/union-childrens-fund-direct-growth",
        "https://groww.in/mutual-funds/union-multi-asset-allocation-fund-direct-growth",
        "https://groww.in/mutual-funds/union-multicap-fund-direct-growth",
        "https://groww.in/mutual-funds/union-gold-etf-fof-direct-growth",
        "https://groww.in/mutual-funds/union-innovation-opportunities-fund-direct-growth",
    ],
    "HDFC Mutual Fund": [
        "https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth",
        "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
        "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
        "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth",
        "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
        "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
        "https://groww.in/mutual-funds/hdfc-short-term-opportunities-fund-direct-growth",
        "https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth",
        "https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth",
        "https://groww.in/mutual-funds/hdfc-pharma-and-healthcare-fund-direct-growth",
    ]
}
```

### 12.2 Scraper Pseudocode

```python
# src/scraper/scraper.py

for amc_name, urls in CORPUS_URLS.items():
    for url in urls:
        html = fetch(url)                    # requests.get or Playwright
        data = parse_fields(html)            # BeautifulSoup selectors
        data["amc"]          = amc_name
        data["source_url"]   = url
        data["scraped_date"] = today()
        save_to_raw(data)                    # data/raw/{amc}/{fund}.json
```

---

## 13. Vector Store Design

```
Vector Store Schema
───────────────────
Each document entry:
  ┌────────────────────────────────────────────────────┐
  │  id:           "hdfc_midcap_chunk_02"              │
  │  vector:       [0.12, -0.43, 0.78, ...]  (768-dim) │
  │  text:         "The expense ratio of HDFC Mid..."  │
  │  metadata:                                         │
  │    source_url:    "https://groww.in/..."           │
  │    fund_name:     "HDFC Mid Cap Fund"              │
  │    amc:           "HDFC Mutual Fund"               │
  │    field:         "expense_ratio"                  │
  │    scraped_date:  "30-Jun-2026"                    │
  └────────────────────────────────────────────────────┘

Query flow:
  1. embed(user_query, prefix="Represent this sentence for searching relevant passages: ")
     →  query_vector (768-dim)
  2. cosine_similarity(query_vector, all_vectors)  [inner product on L2-normalised vecs]
  3. return top-3 by score (threshold ≥ 0.5)
  4. pass (chunk_text + source_url + scraped_date) to LLM
```

---

## 14. Query Classifier Design

The classifier decides whether a query is **factual** (answer it) or **advisory** (refuse it).

### 14.1 Classification Logic (Rule-Based + LLM)

```
Method 1: Keyword / Pattern Matching (fast, no LLM cost)
──────────────────────────────────────────────────────────
  ADVISORY signals:
    - "should I", "which is better", "recommend", "best fund"
    - "will it give", "is it safe", "should I invest"
    - "compare", "vs", "versus", "outperform"

  FACTUAL signals:
    - "what is the expense ratio", "exit load", "SIP amount"
    - "riskometer", "benchmark", "lock-in", "NAV", "category"
    - "how to download", "how to get", "statement"

Method 2: LLM-based classifier (fallback for ambiguous queries)
──────────────────────────────────────────────────────────────
  Prompt: "Is the following query asking for a financial fact
           or financial advice? Reply with FACTUAL or ADVISORY only."
```

### 14.2 Classification Decision Table

| Query Example | Classification | Action |
|---|---|---|
| "What is the expense ratio of Union Midcap Fund?" | FACTUAL | Retrieve & answer |
| "What is the exit load for HDFC Small Cap?" | FACTUAL | Retrieve & answer |
| "Which fund should I invest in?" | ADVISORY | Polite refusal |
| "Is HDFC Mid Cap better than Union Midcap?" | ADVISORY | Polite refusal |
| "What is the riskometer level of HDFC Defence Fund?" | FACTUAL | Retrieve & answer |
| "Will this fund give 20% returns?" | ADVISORY | Polite refusal |

---

## 15. LLM Prompt Design

### 15.1 System Prompt

```
You are a facts-only mutual fund information assistant for Groww.
You ONLY answer questions about mutual fund schemes using the retrieved context below.
You NEVER provide investment advice, fund comparisons, return predictions, or personal recommendations.

Rules:
- Answer in a maximum of 3 sentences.
- Use only information from the provided context — do not hallucinate.
- Always include the source URL provided in the context metadata.
- Always include the scraped date as "Last updated from sources: <date>".
- If the context does not contain the answer, say: "I could not find this information in my current knowledge base."
```

### 15.2 User Prompt Template

```
Context:
{retrieved_chunk_1}
{retrieved_chunk_2}
{retrieved_chunk_3}

Source URLs: {source_url_1}, {source_url_2}
Last scraped: {scraped_date}

User Question: {user_query}

Answer (≤ 3 sentences, facts only, include 1 source URL and last updated date):
```

---

## 16. Privacy & Security Architecture

```
Privacy Boundaries
──────────────────
  ✅ Only public Groww pages are scraped — no authenticated pages
  ✅ No user PII is collected, stored, or transmitted
  ✅ No login required for the assistant
  ✅ No session data persisted beyond the chat window
  ✅ No cookies or tracking

  ❌ Never accept or process:
      - PAN / Aadhaar numbers
      - Bank account or folio numbers
      - OTPs or passwords
      - Email or phone numbers

  If user input contains sensitive data patterns:
      → Log a WARNING (not the data itself)
      → Respond: "Please do not share personal details. I only answer
                  factual questions about mutual fund schemes."
```

---

## 17. Error Handling Strategy

| Error Scenario | Handling |
|---|---|
| URL fetch fails (scraping) | Retry 3x with exponential backoff; log error; skip URL |
| No chunks retrieved (query) | Return: "I could not find relevant information. Please try rephrasing." |
| LLM API error | Return fallback: "Service temporarily unavailable. Please try again." |
| Query too short / empty | Prompt: "Please type a complete question about a mutual fund scheme." |
| Similarity score below threshold | Treat as no-result, return not-found message |
| Advisory query detected | Return polite refusal with AMFI/SEBI link |

---

## 18. Known Limitations

| Limitation | Detail |
|---|---|
| **Static corpus** | Data is scraped once; re-indexing required for updates (NAV changes daily) |
| **No live NAV** | Real-time NAV is not fetched; only the NAV present at scrape time |
| **20 schemes only** | Only the 20 selected schemes (10 Union + 10 HDFC) are in scope |
| **English only** | No multilingual support |
| **No account queries** | Cannot answer personal account-level or portfolio questions |
| **Groww layout changes** | If Groww updates its HTML structure, scraper selectors may break |
| **LLM hallucination risk** | Mitigated by strict prompt instructions + similarity threshold, but not zero |
| **Groww URLs only** | Corpus is strictly the 20 Groww scheme pages provided — no PDFs, no AMC websites, no other external sources |

---

*Architecture document for: Groww Mutual Fund FAQ RAG Chatbot*
*Generated from: [context.md](./context.md) | [problemstatement.txt](./problemstatement.txt)*
*Last updated: 2026-06-30*
