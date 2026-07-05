# Implementation Plan: Groww Mutual Fund FAQ RAG Chatbot

> **Version**: 1.0.0 | **Created**: 2026-06-30 | **AMCs**: Union Mutual Fund & HDFC Mutual Fund
> **Reference Docs**: [context.md](./context.md) | [architecture.md](./architecture.md)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Phases Overview](#2-project-phases-overview)
3. [Phase 0: Environment Setup](#phase-0-environment-setup)
4. [Phase 1: Data Scraping & Ingestion](#phase-1-data-scraping--ingestion)
5. [Phase 2: Text Chunking](#phase-2-text-chunking)
6. [Phase 3: Embedding](#phase-3-embedding)
7. [Phase 4: Vector Store Indexing](#phase-4-vector-store-indexing)
8. [Phase 5: Query Classifier](#phase-5-query-classifier)
9. [Phase 6: Retrieval Engine](#phase-6-retrieval-engine)
10. [Phase 7: LLM Response Generation](#phase-7-llm-response-generation)
11. [Phase 8: User Interface](#phase-8-user-interface)
12. [Phase 9: Integration & End-to-End Testing](#phase-9-integration--end-to-end-testing)
13. [Phase 10: Final Polish & Documentation](#phase-10-final-polish--documentation)
14. [Phase 11: Automated Data Ingestion Scheduler](#phase-11-automated-data-ingestion-scheduler)
15. [14. Dependency Map](#14-dependency-map)
16. [15. File Deliverable Checklist](#15-file-deliverable-checklist)
17. [16. Risk Register](#16-risk-register)
18. [17. Success Criteria Checklist](#17-success-criteria-checklist)

---

## 1. Executive Summary

This plan outlines the step-by-step implementation of the **Groww Mutual Fund FAQ RAG Chatbot** — a facts-only assistant that retrieves and presents structured mutual fund information from a curated corpus of 20 Groww scheme pages (10 Union MF + 10 HDFC MF).

The system is built in **three distinct phases**:
- **Offline / Build-time**: Scraping → Chunking → Embedding → Vector Store Index
- **Online / Runtime**: User Query → Classifier → Retriever → LLM → Response
- **Scheduled / Maintenance**: Daily execution of the Offline pipeline for fresh data

Total phases: **11** | Total estimated tasks: **48**

---

## 2. Project Phases Overview

The pipeline has two tracks that merge at the end:

- **Offline (Build-time):** Environment Setup → Scraping → Chunking → Embedding → Vector Store
- **Online (Runtime):** User Query → Classifier → Retriever → LLM → Response → UI

Phase 5 (Classifier) is independent of the scraping pipeline and can be built in parallel with Phases 1–4.

---

## Phase 0: Environment Setup

### Goal
Set up the project repository, virtual environment, folder structure, and all dependencies before writing any functional code.

### Tasks

#### 0.1 — Create Project Directory Structure
Create the standard project layout with `docs/`, `data/raw/`, `data/chunks/`, `data/vector_store/`, `src/scraper/`, `src/ingestion/`, `src/retrieval/`, `src/generation/`, `src/app/`, and `scripts/`.

#### 0.2 — Create Python Virtual Environment
Create a Python virtual environment using `python -m venv venv` and activate it. Python 3.10+ is required.

#### 0.3 — Install Dependencies
Install all packages from `requirements.txt`, which covers scraping, text processing, vector store, LLM APIs, and the web UI framework.

#### 0.4 — Create `.env` File
Copy `.env.example` to `.env` and populate it with:
- `GROQ_API_KEY` — for the primary LLM (Groq, free tier)
- `GEMINI_API_KEY` — for the fallback LLM (Google Gemini Flash, free tier)
- `LLM_PROVIDER` — set to `groq` by default; switch to `gemini` if quota is exceeded

#### 0.5 — Define Scraper Target URLs
Create `src/scraper/urls.py` containing the list of 20 Groww scheme URLs (10 Union MF, 10 HDFC MF) that form the entire knowledge corpus.

### Acceptance Criteria
- [x] All directories created successfully
- [x] Virtual environment active with no import errors
- [x] `.env` file populated with valid API keys
- [x] `src/scraper/urls.py` contains 20 URLs

---

## Phase 1: Data Scraping & Ingestion

### Goal
Scrape all 20 Groww mutual fund scheme pages and save raw structured data as JSON files, one per fund. The scraper must handle both static and JavaScript-rendered pages.

### Tasks

#### 1.1 — Implement `scraper.py` (Primary: requests + BeautifulSoup)
The primary scraper uses `requests` to fetch the raw HTML and `BeautifulSoup` to extract the following fields from each Groww scheme page:
- Fund name
- NAV (Net Asset Value)
- Expense ratio
- Exit load
- Minimum SIP amount
- Riskometer rating
- Benchmark index
- AMC name

Each fund's data is saved as a JSON file in `data/raw/union/` or `data/raw/hdfc/` with the filename matching the fund's slug.

#### 1.2 — Implement `playwright_scraper.py` (Fallback: JavaScript-rendered pages)
For pages that require JavaScript execution to render content, a Playwright-based fallback scraper is implemented. It launches a headless Chromium browser, waits for the page to fully load, and then runs the same extraction logic as the primary scraper.

#### 1.3 — Implement Scraper Orchestration
An orchestrator script (`scripts/run_scraper.py`) iterates through all 20 URLs, attempts the primary scraper, and falls back to Playwright on failure. It adds a 1-second polite delay between each request.

#### 1.4 — Validate Raw Data
A validation script (`scripts/validate_raw.py`) checks that all 20 JSON files exist and contain non-empty values for all required fields. It flags any missing or `null` fields for manual review.

### Acceptance Criteria
- [x] 20 JSON files exist in `data/raw/`
- [x] All files contain the required fields (fund name, expense ratio, exit load, minimum SIP, riskometer)
- [x] No PII found in raw data files

---

## Phase 2: Text Chunking

### Goal
Convert the raw JSON data into structured, self-contained text chunks suitable for embedding and retrieval. Each chunk must be semantically meaningful and carry complete metadata.

### Tasks

#### 2.1 — Design Chunk Strategy
Each fund's JSON is decomposed into **one chunk per field** (e.g., one chunk for expense ratio, one for exit load). This field-level chunking ensures that retrieval is precise and does not mix different data points in one chunk.

Each chunk contains:
- `chunk_id`: Unique identifier (e.g., `union_midcap_expense_ratio`)
- `text`: A human-readable sentence describing the field value (e.g., *"The expense ratio of Union Midcap Fund is 1.05%."*)
- `source_url`: The Groww URL the data was scraped from
- `fund_name`: Full fund name
- `amc`: AMC name (Union MF or HDFC MF)
- `field`: The field type (e.g., `expense_ratio`)
- `scraped_date`: The date the page was scraped

#### 2.2 — Implement `chunker.py`
Reads all raw JSON files and converts each field into a text chunk following the template above. Saves all chunks as a single `data/chunks/chunks.json` file.

#### 2.3 — Validate Chunks
A validation script (`scripts/validate_chunks.py`) checks:
- Total chunk count is as expected (approximately 8–10 chunks per fund × 20 funds = 160–200 chunks)
- No chunk has an empty `text` field
- All chunks carry a valid `source_url`

### Acceptance Criteria
- [x] `data/chunks/chunks.json` exists with 160+ chunks
- [x] Every chunk has non-empty `text`, `source_url`, and `fund_name`
- [x] Chunk text is a complete, readable sentence

---

## Phase 3: Embedding

### Goal
Generate vector embeddings for all text chunks using the BGE embedding model (`BAAI/bge-base-en-v1.5`). Embeddings are stored as a NumPy array for indexing in Phase 4.

### Tasks

#### 3.1 — Load Embedding Model
The model `BAAI/bge-base-en-v1.5` is loaded via `sentence-transformers`. It produces **768-dimensional** embeddings. The model is cached locally after the first download.

**Important**: BGE requires a query instruction prefix at runtime:
`"Represent this sentence for searching relevant passages: " + query_text`

This prefix is **only applied to user queries at retrieval time**, not to the document chunks during indexing.

#### 3.2 — Implement `embedder.py`
Reads all chunks from `data/chunks/chunks.json`, extracts the `text` field from each chunk, and encodes them using the BGE model with `batch_size=32`. Saves the resulting embeddings as `data/chunks/embeddings.npy`.

#### 3.3 — Run Embedding Script
The script `scripts/embed_chunks.py` orchestrates the embedding process and logs progress.

### Acceptance Criteria
- [x] `data/chunks/embeddings.npy` exists
- [x] Shape is `(N, 768)` where N equals the chunk count
- [x] No NaN or zero vectors present

---

## Phase 4: Vector Store Indexing

### Goal
Load the embeddings into a FAISS vector index for fast cosine-similarity search at runtime. Persist the index and metadata to disk.

### Tasks

#### 4.1 — Implement `indexer.py`
Loads `embeddings.npy` and `chunks.json`, builds a FAISS `IndexFlatIP` (inner product for cosine similarity on L2-normalized vectors), adds all embeddings, and saves:
- `data/vector_store/index.faiss` — the FAISS binary index
- `data/vector_store/metadata.pkl` — a pickled list of chunk metadata dicts (same order as the index)

#### 4.2 — Run Indexer Script
The script `scripts/build_index.py` orchestrates index building and prints a summary of total vectors stored.

### Acceptance Criteria
- [x] `data/vector_store/index.faiss` exists and is non-empty
- [x] `data/vector_store/metadata.pkl` exists with the correct number of entries
- [x] A test search returns a relevant result

---

## Phase 5: Query Classifier

### Goal
Build a lightweight rule-based classifier that determines whether a user's query is a valid **factual question** that should be passed to the retrieval engine, or an **advisory/speculative question** that should trigger a refusal response.

### Tasks

#### 5.1 — Define Classification Rules
The classifier uses keyword matching and heuristics, not a trained ML model:
- **Factual** queries contain keywords like: `expense ratio`, `exit load`, `SIP`, `NAV`, `riskometer`, `benchmark`, `lock-in`, `minimum investment`, `returns` (factual, not predictive)
- **Advisory** queries contain keywords like: `should I`, `better`, `compare`, `recommend`, `safe for me`, `which is best`, `predict`, `will it grow`

#### 5.2 — Implement `classifier.py`
Implements a `QueryClassifier` class with an `is_factual(query: str) -> bool` method. Returns `True` if the query passes the factual check, `False` otherwise.

#### 5.3 — Write Unit Tests
`tests/test_classifier.py` contains at least 10 test cases covering:
- Factual queries that should return `True`
- Advisory queries that should return `False`
- Edge cases (e.g., short queries, queries with both factual and advisory elements)

### Acceptance Criteria
- [x] Classifier correctly identifies factual queries
- [x] Classifier correctly refuses advisory/comparative queries
- [x] Unit tests pass with ≥ 90% accuracy on the test set

---

## Phase 6: Retrieval Engine

### Goal
Build the retrieval module that embeds a user query, searches the FAISS index for the top-k most relevant chunks, and returns them along with their metadata.

### Tasks

#### 6.1 — Implement `retriever.py`
Implements a `Retriever` class that:
1. Loads the FAISS index and metadata from disk on initialization
2. Accepts a user query string
3. Prepends the BGE query instruction prefix to the query
4. Embeds the query using the same BGE model used in Phase 3
5. Searches the FAISS index for the **top-k=3** most similar chunks
6. Filters out any results with a cosine similarity score below **0.5** (to prevent hallucination from irrelevant results)
7. Returns a list of `{text, source_url, fund_name, amc, scraped_date}` dicts

#### 6.2 — Run Retrieval Test Script
`scripts/test_search.py` runs a set of test queries against the retriever and prints the retrieved chunks and their similarity scores for manual inspection.

### Acceptance Criteria
- [x] Retriever returns the correct fund data for a known query
- [x] Low-relevance queries (similarity < 0.5) return an empty list
- [x] Retriever loads from disk correctly on a cold start

---

## Phase 7: LLM Response Generation

### Goal
Build the LLM response layer that takes the user's query and the retrieved chunks as context, and generates a concise, citation-backed factual answer using a free-tier LLM.

### Tasks

#### 7.1 — Implement `prompt_templates.py`
Defines the system prompt and the user-turn template. The system prompt strictly instructs the LLM to:
- Answer in ≤ 3 sentences using only the provided context
- Never include opinions, comparisons, or investment advice
- Always cite exactly one source URL from the context
- Append a "Last updated from sources: DD-MMM-YYYY" footer

#### 7.2 — Implement `llm.py`
Provides a unified `LLMClient` class with a `generate(prompt: str) -> str` method. On initialization, it reads `LLM_PROVIDER` from the `.env` file and routes to:
- **Groq Llama3-8b** (`groq`) if `LLM_PROVIDER=groq`
- **Gemini Flash** (`google-generativeai`) if `LLM_PROVIDER=gemini`

This allows switching providers without any code change — only an `.env` update is needed.

#### 7.3 — Implement `response_builder.py`
The main orchestration class that ties everything together:
1. Accepts a user query
2. Runs the `QueryClassifier` — if advisory, returns the refusal response immediately
3. If factual, runs the `Retriever` to get top-k chunks
4. If no chunks pass the similarity threshold, returns a "not found" fallback message
5. Constructs the full prompt using the templates and retrieved context
6. Calls the `LLMClient.generate()` method
7. Returns a structured response dict: `{response, source_url, scraped_date}`

### Refusal Response
When the classifier flags a query as advisory or non-factual, the system immediately skips retrieval and returns a fixed polite refusal message. The refusal tells the user that the assistant only answers factual questions, cannot give investment advice or comparisons, and directs them to ask a specific factual question about a Union MF or HDFC MF scheme instead.

### Acceptance Criteria
- [x] A factual query produces a response with ≤ 3 sentences, 1 source URL, and a date
- [x] An advisory query returns the exact refusal template
- [x] An out-of-scope query returns the "not found" fallback
- [x] Switching `LLM_PROVIDER` in `.env` works without code changes

---

## Phase 8: User Interface

### Goal
Build a premium, modern **Google Stitch** chat interface (for desktops only) with a disclaimer banner, welcome message, example questions, and real-time chatting.

The UI is built as a lightweight frontend deployed on **Vercel**. It communicates with a **FastAPI** backend deployed on **Railway**, which exposes a `/api/chat` endpoint connected to the `ResponseBuilder` from Phase 7.

### Tasks

#### 8.1 — Generate UI with Google Stitch
Use the Google Stitch tool to generate a polished, desktop-optimized HTML/CSS/JS chat interface matching the Groww design language. The generated `code.html` is placed at `src/app/static/index.html`.

#### 8.2 — Create `src/app/main.py` (FastAPI Backend)
The FastAPI app:
- Serves `src/app/static/index.html` at the root route `GET /`
- Exposes `POST /api/chat` which accepts `{"query": "..."}` and returns `{"response": "...", "source_url": "...", "scraped_date": "..."}`
- Uses `ResponseBuilder` internally to process each query

#### 8.3 — Wire Frontend to Backend
Modify the `<script>` block in `index.html` to:
- Listen for Send button clicks and Enter key presses
- Hide the welcome card on the first message
- Dynamically append user and assistant chat bubbles to the DOM
- Call `fetch('/api/chat', ...)` to get the real RAG response
- Display the response text, source link, and "Last updated" date in the assistant bubble
- Show a "Thinking..." loading state while waiting for the API response

#### 8.4 — Run and Validate UI Locally
Start the server with `uvicorn src.app.main:app --reload`, open `http://127.0.0.1:8000` in a browser, and manually verify:

- Disclaimer banner is visible and sticky at the top
- Welcome card shows 3 example questions as clickable pills
- Clicking a pill auto-populates the input and sends the message
- Chat input accepts typed queries on Enter or Send button
- Responses appear with a clean source URL and date footer
- Advisory queries correctly trigger the refusal message

### Acceptance Criteria
- [x] UI launches at `http://127.0.0.1:8000` without errors
- [x] Disclaimer banner is always visible
- [x] 3 example questions shown on welcome card
- [x] Factual queries return real answers from the RAG backend
- [x] Advisory queries display the refusal message

---

## Phase 9: Integration & End-to-End Testing

### Goal
Run a full end-to-end test suite that validates the entire pipeline from user query to rendered response, covering all happy paths, edge cases, and failure modes.

### Tasks

#### 9.1 — Write `tests/test_e2e.py`
End-to-end tests covering:
- At least 5 factual queries across different funds and field types
- At least 3 advisory queries that must trigger refusal
- An out-of-scope query (e.g., about a fund not in the corpus)
- A gibberish/empty query

Each test checks the response structure (text length, presence of source URL, presence of date) and does a keyword spot-check on the answer.

#### 9.2 — Run Full Pipeline Test
Execute `pytest tests/` and confirm all tests pass. Review any failures and fix edge cases in the classifier, retriever, or response builder as needed.

#### 9.3 — Manual Acceptance Review
Manually run at least 10 diverse queries through the live UI and verify:
- Correctness of all returned facts
- All source URLs resolve and are correct
- All scraped dates are accurate

### Acceptance Criteria
- [x] All E2E tests pass with `pytest tests/`
- [x] Manual review passes for 10/10 diverse queries
- [x] No hallucinated facts detected

---

## Phase 10: Final Polish & Documentation

### Goal
Polish the codebase, finalize documentation, clean up temporary files, and produce a complete, well-documented project ready for submission or handoff.

### Tasks

#### 10.1 — Update `README.md`
Write a comprehensive README covering:
- Project overview and problem statement
- Architecture diagram (text-based, copied from `architecture.md`)
- Setup and installation instructions
- How to run the scraper, build the index, and start the UI server
- How to switch between Gemini and Groq LLM providers
- Corpus details (which 20 funds are covered)

#### 10.2 — Code Cleanup
- Remove all `print()` debug statements; replace with proper `logging`
- Add docstrings to all public classes and methods
- Ensure all files have correct module-level comments

#### 10.3 — Final File Audit
Verify every file in the File Deliverable Checklist (Section 15) exists and is non-empty.

#### 10.4 — Clean Up Temporary Files
Remove `ui_temp/` directory and any other temporary files created during development.

### Acceptance Criteria
- [x] README is complete and accurate
- [x] All source files have docstrings
- [x] No debug print statements remain
- [x] All deliverable files are present

---

## Phase 11: Automated Data Ingestion Scheduler

### Goal
Implement a scheduler component to automatically trigger the entire offline data ingestion pipeline (scraping, chunking, embedding, indexing) every day. This ensures the vector store is always up-to-date with the latest NAVs and mutual fund metadata.

### Tasks

#### 11.1 — Create GitHub Actions Workflow
Create `.github/workflows/schedule_ingestion.yml` to define a cron job that runs daily at 10:30 AM IST (05:00 AM UTC). The workflow will set up Python, install dependencies, and run the `scripts/run_pipeline.py` orchestrator script to execute the entire end-to-end ingestion pipeline.

#### 11.2 — Automate Vector Store Commit (Optional)
Configure the workflow to commit the newly generated FAISS index and metadata back to the repository so the live application can pull the latest data upon its next deployment, or set up a trigger to deploy the updated data to the hosting provider.

### Acceptance Criteria
- [x] `.github/workflows/schedule_ingestion.yml` is created and valid
- [x] Workflow correctly runs `build_index.py` via a cron schedule
- [x] Workflow handles environment variables and API keys securely using GitHub Secrets

---

## 14. Dependency Map

The scraping pipeline (Phases 1–4) must complete before the retrieval engine (Phase 6) can work. The classifier (Phase 5) is independent and can be built anytime after the environment is set up. Both the classifier and the retrieval engine must be ready before the LLM generator (Phase 7) can be assembled. The UI (Phase 8) depends on Phase 7, testing (Phase 9) depends on the UI, and final documentation (Phase 10) comes last.

---

## 15. File Deliverable Checklist

| File | Phase | Status |
|---|---|---|
| `requirements.txt` | Phase 0 | ☑ |
| `.env.example` | Phase 0 | ☑ |
| `src/scraper/urls.py` | Phase 0 | ☑ |
| `src/scraper/scraper.py` | Phase 1 | ☑ |
| `src/scraper/playwright_scraper.py` | Phase 1 | ☑ |
| `scripts/validate_raw.py` | Phase 1 | ☑ |
| `data/raw/union_mutual_fund/*.json` (10 files) | Phase 1 | ☑ |
| `data/raw/hdfc_mutual_fund/*.json` (10 files) | Phase 1 | ☑ |
| `src/ingestion/chunker.py` | Phase 2 | ☑ |
| `scripts/validate_chunks.py` | Phase 2 | ☑ |
| `data/chunks/chunks.json` | Phase 2 | ☑ |
| `src/ingestion/embedder.py` | Phase 3 | ☑ |
| `scripts/embed_chunks.py` | Phase 3 | ☑ |
| `data/chunks/embeddings.npy` | Phase 3 | ☑ |
| `src/ingestion/indexer.py` | Phase 4 | ☑ |
| `scripts/build_index.py` | Phase 4 | ☑ |
| `data/vector_store/index.faiss` | Phase 4 | ☑ |
| `data/vector_store/metadata.pkl` | Phase 4 | ☑ |
| `src/retrieval/classifier.py` | Phase 5 | ☑ |
| `tests/test_classifier.py` | Phase 5 | ☑ |
| `src/retrieval/retriever.py` | Phase 6 | ☑ |
| `scripts/test_retrieval.py` | Phase 6 | ☑ |
| `src/generation/prompt_templates.py` | Phase 7 | ☑ |
| `src/generation/llm.py` | Phase 7 | ☑ |
| `src/generation/response_builder.py` | Phase 7 | ☑ |
| `src/app/static/index.html` | Phase 8 | ☑ |
| `src/app/main.py` | Phase 8 | ☑ |
| `tests/test_e2e.py` | Phase 9 | [x] |
| `README.md` | Phase 10 | [x] |
| `.github/workflows/schedule_ingestion.yml` | Phase 11 | [x] |

---

## 16. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Groww page HTML structure changes | Medium | High | CSS selectors + fallback Playwright; validate after each scrape |
| Groww blocks scraper (rate limiting) | Medium | Medium | Polite 1-sec delay, retry logic, descriptive User-Agent header |
| LLM hallucination despite strict prompt | Low | High | Similarity threshold ≥ 0.5, strict system prompt, "not found" fallback |
| Groq API quota exceeded | Very Low | Low | Switch `LLM_PROVIDER=gemini` in `.env` — zero code changes needed |
| Gemini API quota exceeded | Low | Medium | Switch back to `LLM_PROVIDER=groq`; both are free-tier |
| BGE model download fails | Very Low | Medium | Model cached after first download; use offline if needed |
| JS-rendered data not captured by `requests` | Medium | High | Playwright fallback implemented in Phase 1 |
| Empty retrieval (no relevant chunk) | Low | Low | Graceful "not found" response; user prompted to rephrase |
| PII accidentally captured in scrape | Very Low | Very High | Validation regex scan on all `data/raw/` files post-scrape |

---

## 17. Success Criteria Checklist

Mapped directly from `context.md § 11`:

| Criterion | Verification Method | Status |
|---|---|---|
| ✅ Retrieval Accuracy | E2E test: top result fund name matches query fund | ☑ |
| ✅ Response Compliance | Manual review: ≤ 3 sentences, 1 citation, date present | ☑ |
| ✅ Refusal Accuracy | E2E test: advisory queries trigger refusal template | ☑ |
| ✅ Privacy Safety | Grep audit on `data/` for PII patterns | ☑ |
| ✅ UI Quality | Manual: disclaimer visible, example questions shown | ☑ |
| ✅ Source Traceability | Every factual response has valid Groww URL | ☑ |

---

*Implementation Plan for: Groww Mutual Fund FAQ RAG Chatbot*
*Reference Docs: [context.md](./context.md) | [architecture.md](./architecture.md)*
*Last updated: 2026-06-30 — Chunking & Embedding split into separate phases; BGE embedding (BAAI/bge-base-en-v1.5, 768-dim); Groq (llama3-8b-8192) replaces OpenAI as free LLM fallback. Phase 8 UI changed from Streamlit to Google Stitch (desktop-only) served via FastAPI.*
