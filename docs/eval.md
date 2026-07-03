# Evaluation Guide: Groww Mutual Fund FAQ RAG Chatbot

> **Version**: 1.0.0 | **Created**: 2026-06-30 | **Scope**: Phase 0 – Phase 10
> **Reference Docs**: [implementationplan.md](./implementationplan.md) | [architecture.md](./architecture.md) | [edge-cases.md](./edge-cases.md)

---

## Table of Contents

1. [Phase 0 — Environment Setup](#phase-0--environment-setup)
2. [Phase 1 — Data Scraping & Ingestion](#phase-1--data-scraping--ingestion)
3. [Phase 2 — Text Chunking](#phase-2--text-chunking)
4. [Phase 3 — Embedding](#phase-3--embedding)
5. [Phase 4 — Vector Store Indexing](#phase-4--vector-store-indexing)
6. [Phase 5 — Query Classifier](#phase-5--query-classifier)
7. [Phase 6 — Retrieval Engine](#phase-6--retrieval-engine)
8. [Phase 7 — LLM Response Generation](#phase-7--llm-response-generation)
9. [Phase 8 — User Interface](#phase-8--user-interface)
10. [Phase 9 — Integration & End-to-End Testing](#phase-9--integration--end-to-end-testing)
11. [Phase 10 — Final Polish & Documentation](#phase-10--final-polish--documentation)
12. [Overall Evaluation Scorecard](#overall-evaluation-scorecard)

---

## Phase 0 — Environment Setup

**Goal**: Confirm the project skeleton, virtual environment, dependencies, and configuration are ready before any functional code is written.

---

### Eval-0.1 — Directory Structure

**Method**: Manual file-system check

```bash
# Run from project root
python -c "
import os
required = [
    'docs', 'data/raw/union', 'data/raw/hdfc', 'data/chunks',
    'data/vector_store', 'src/scraper', 'src/ingestion',
    'src/retrieval', 'src/generation', 'src/app', 'scripts'
]
for d in required:
    status = '✅' if os.path.isdir(d) else '❌ MISSING'
    print(f'{status}  {d}')
"
```

| Check | Pass Condition |
|---|---|
| All 12 directories exist | `✅` for every directory listed |
| `requirements.txt` present at root | `os.path.isfile('requirements.txt')` → `True` |
| `.env.example` present at root | `os.path.isfile('.env.example')` → `True` |
| `README.md` present at root | `os.path.isfile('README.md')` → `True` |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-0.2 — Dependency Installation

**Method**: Install and verify all packages import cleanly

```bash
pip install -r requirements.txt
python -c "
import requests, bs4, langchain, sentence_transformers
import faiss, streamlit, dotenv, tqdm
import google.generativeai, groq
print('✅ All required packages import successfully')
"
```

| Check | Pass Condition |
|---|---|
| `pip install` exits with code 0 | No `ERROR` lines in output |
| All 9 import groups succeed | No `ModuleNotFoundError` |
| FAISS usable | `faiss.IndexFlatIP(768)` runs without error |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-0.3 — `.env.example` Completeness

**Method**: Manual inspection

```bash
python -c "
with open('.env.example') as f:
    content = f.read()
required_keys = ['GEMINI_API_KEY', 'GROQ_API_KEY', 'LLM_PROVIDER',
                 'TOP_K_RETRIEVAL', 'SIMILARITY_THRESHOLD',
                 'VECTOR_STORE_TYPE', 'EMBEDDING_MODEL']
for k in required_keys:
    status = '✅' if k in content else '❌ MISSING'
    print(f'{status}  {k}')
"
```

| Check | Pass Condition |
|---|---|
| All 7 required keys present | `✅` for all |
| Values are placeholders only | No real API keys committed |
| `EMBEDDING_MODEL=BAAI/bge-base-en-v1.5` present | Exact string match |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-0.4 — Corpus URL Registry

**Method**: Automated check

```python
# scripts/eval/eval_phase0.py
from src.scraper.urls import CORPUS_URLS

all_urls = [u for urls in CORPUS_URLS.values() for u in urls]

assert len(CORPUS_URLS) == 2,                         "❌ Expected exactly 2 AMCs"
assert "Union Mutual Fund" in CORPUS_URLS,            "❌ Union MF key missing"
assert "HDFC Mutual Fund" in CORPUS_URLS,             "❌ HDFC MF key missing"
assert len(CORPUS_URLS["Union Mutual Fund"]) == 10,   "❌ Union MF must have 10 URLs"
assert len(CORPUS_URLS["HDFC Mutual Fund"]) == 10,    "❌ HDFC MF must have 10 URLs"
assert len(set(all_urls)) == 20,                      "❌ Duplicate URLs detected"
assert all(u.startswith("https://groww.in/mutual-funds/") for u in all_urls), \
                                                      "❌ All URLs must be Groww mutual fund URLs"
print("✅ Eval-0.4 PASSED — 20 unique Groww URLs correctly registered")
```

| Check | Pass Condition |
|---|---|
| Exactly 2 AMC keys | `len(CORPUS_URLS) == 2` |
| 10 URLs per AMC | Both lists have `len == 10` |
| All 20 URLs unique | `len(set(all_urls)) == 20` |
| All URLs from `groww.in/mutual-funds/` | Prefix check passes |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Phase 0 Evaluation Summary

| Eval ID | Description | Result |
|---|---|---|
| Eval-0.1 | Directory structure complete | ☐ |
| Eval-0.2 | All dependencies install & import | ☐ |
| Eval-0.3 | `.env.example` has all required keys | ☐ |
| Eval-0.4 | 20 unique Groww URLs registered | ☐ |

> **Phase 0 Gate**: All 4 checks must pass before proceeding to Phase 1.

---

## Phase 1 — Data Scraping & Ingestion

**Goal**: Confirm the scraper successfully fetches and extracts structured data from all 20 Groww fund URLs.

---

### Eval-1.1 — Raw JSON File Count

**Method**: File system check after running `build_index.py` or the scraper

```python
# scripts/eval/eval_phase1.py
import glob, json

union_files = glob.glob("data/raw/union_mutual_fund/*.json")
hdfc_files  = glob.glob("data/raw/hdfc_mutual_fund/*.json")

assert len(union_files) == 10, f"❌ Expected 10 Union JSON files, got {len(union_files)}"
assert len(hdfc_files)  == 10, f"❌ Expected 10 HDFC JSON files, got {len(hdfc_files)}"
print(f"✅ Eval-1.1 PASSED — {len(union_files)} Union + {len(hdfc_files)} HDFC JSON files found")
```

| Check | Pass Condition |
|---|---|
| 10 JSON files under `data/raw/union_mutual_fund/` | `len == 10` |
| 10 JSON files under `data/raw/hdfc_mutual_fund/` | `len == 10` |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-1.2 — Required Fields Present in Every JSON

**Method**: Field completeness validation

```python
required_fields = ["fund_name", "amc", "category", "nav", "expense_ratio",
                   "exit_load", "min_sip", "riskometer", "benchmark",
                   "lock_in", "source_url", "scraped_date"]
critical_fields = ["fund_name", "expense_ratio", "exit_load", "riskometer", "source_url"]

failures = []
for path in glob.glob("data/raw/**/*.json", recursive=True):
    with open(path) as f:
        data = json.load(f)
    missing_all      = [k for k in required_fields if k not in data]
    missing_critical = [k for k in critical_fields if not data.get(k)]
    if missing_all or missing_critical:
        failures.append({"file": path, "missing_all": missing_all, "missing_critical": missing_critical})

if failures:
    for f in failures:
        print(f"❌ {f['file']}: {f}")
else:
    print("✅ Eval-1.2 PASSED — All 20 JSON files have all required fields")
```

| Check | Pass Condition |
|---|---|
| All 12 fields present in every file | 0 `missing_all` entries |
| 5 critical fields non-empty | 0 `missing_critical` entries |
| `source_url` is a valid Groww URL | Starts with `https://groww.in/mutual-funds/` |
| `scraped_date` formatted `DD-MMM-YYYY` | Regex match `\d{2}-[A-Z][a-z]{2}-\d{4}` |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-1.3 — AMC Field Matches File Path

**Method**: Cross-check `amc` value against directory name

```python
for path in glob.glob("data/raw/union_mutual_fund/*.json"):
    with open(path) as f: data = json.load(f)
    assert data["amc"] == "Union Mutual Fund", f"❌ AMC mismatch in {path}"

for path in glob.glob("data/raw/hdfc_mutual_fund/*.json"):
    with open(path) as f: data = json.load(f)
    assert data["amc"] == "HDFC Mutual Fund", f"❌ AMC mismatch in {path}"

print("✅ Eval-1.3 PASSED — AMC field matches directory for all 20 files")
```

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-1.4 — No PII in Scraped Data

**Method**: Regex audit on all raw JSON files

```python
import re

PII_PATTERNS = {
    "PAN":     r"[A-Z]{5}[0-9]{4}[A-Z]",
    "Aadhaar": r"\b[0-9]{12}\b",
    "Phone":   r"\b[6-9][0-9]{9}\b",
}

pii_found = []
for path in glob.glob("data/raw/**/*.json", recursive=True):
    with open(path) as f:
        content = f.read()
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, content):
            pii_found.append({"file": path, "type": pii_type})

assert len(pii_found) == 0, f"❌ PII detected: {pii_found}"
print("✅ Eval-1.4 PASSED — 0 PII patterns found in raw data")
```

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Phase 1 Evaluation Summary

| Eval ID | Description | Result |
|---|---|---|
| Eval-1.1 | 20 JSON files created (10+10) | ☐ |
| Eval-1.2 | All required fields present & non-empty | ☐ |
| Eval-1.3 | AMC field matches directory path | ☐ |
| Eval-1.4 | Zero PII patterns in raw data | ☐ |

> **Phase 1 Gate**: All 4 checks must pass before proceeding to Phase 2.

---

## Phase 2 — Text Chunking

**Goal**: Confirm raw JSON records are correctly converted to text chunks with metadata.

---

### Eval-2.1 — Chunk File Exists and Is Valid JSON

```python
import json

with open("data/chunks/chunks.json") as f:
    chunks = json.load(f)

assert isinstance(chunks, list), "❌ chunks.json must be a JSON array"
assert len(chunks) >= 60,  f"❌ Expected ≥ 60 chunks, got {len(chunks)}"
assert len(chunks) <= 120, f"❌ Expected ≤ 120 chunks, got {len(chunks)}"
print(f"✅ Eval-2.1 PASSED — {len(chunks)} chunks loaded from chunks.json")
```

| Check | Pass Condition |
|---|---|
| File exists and is valid JSON | No `JSONDecodeError` |
| Chunk count between 60 and 120 | `60 ≤ len(chunks) ≤ 120` |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-2.2 — All 20 Funds Represented

```python
fund_names = set(c["fund_name"] for c in chunks)
assert len(fund_names) == 20, \
    f"❌ Expected 20 distinct fund names, got {len(fund_names)}: {fund_names}"
print(f"✅ Eval-2.2 PASSED — All 20 funds present in chunks")
```

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-2.3 — Chunk Metadata Schema Completeness

```python
required_chunk_fields = ["chunk_id", "text", "source_url", "fund_name", "amc", "scraped_date"]
failures = []
for c in chunks:
    missing = [k for k in required_chunk_fields if not c.get(k)]
    if missing:
        failures.append({"chunk_id": c.get("chunk_id", "UNKNOWN"), "missing": missing})

assert len(failures) == 0, f"❌ {len(failures)} chunks have missing fields: {failures[:3]}"
print("✅ Eval-2.3 PASSED — All chunks have complete metadata")
```

| Check | Pass Condition |
|---|---|
| All 6 metadata fields present | `missing == []` for every chunk |
| `text` field non-empty | `len(c["text"].strip()) > 0` for all chunks |
| `source_url` is a Groww URL | Starts with `https://groww.in/mutual-funds/` |
| `chunk_id` values are unique | `len(set(ids)) == len(ids)` |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-2.4 — Chunk Size Within Bounds

```python
oversized  = [c for c in chunks if len(c["text"]) > 600]
undersized = [c for c in chunks if len(c["text"]) < 10]

assert len(oversized)  == 0, f"❌ {len(oversized)} chunks exceed 600 chars"
assert len(undersized) == 0, f"❌ {len(undersized)} chunks are < 10 chars (likely empty)"
avg_size = sum(len(c["text"]) for c in chunks) / len(chunks)
print(f"✅ Eval-2.4 PASSED — Avg chunk size: {avg_size:.0f} chars (all within bounds)")
```

| Check | Pass Condition |
|---|---|
| No chunk exceeds 600 characters | `len(oversized) == 0` |
| No chunk is fewer than 10 characters | `len(undersized) == 0` |
| Average chunk size 300–550 chars | Within expected range |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Phase 2 Evaluation Summary

| Eval ID | Description | Result |
|---|---|---|
| Eval-2.1 | `chunks.json` valid, 60–120 chunks | ☐ |
| Eval-2.2 | All 20 fund names present | ☐ |
| Eval-2.3 | All 6 metadata fields complete | ☐ |
| Eval-2.4 | Chunk sizes within bounds | ☐ |

> **Phase 2 Gate**: All 4 checks must pass before proceeding to Phase 3.

---

## Phase 3 — Embedding

**Goal**: Confirm BGE embeddings are generated correctly with the expected shape and quality.

---

### Eval-3.1 — Embedding File Shape

```python
import numpy as np

vectors = np.load("data/chunks/embeddings.npy")

assert vectors.ndim == 2,             f"❌ Expected 2D array, got {vectors.ndim}D"
assert vectors.shape[1] == 768,       f"❌ Expected 768 dims (BGE base), got {vectors.shape[1]}"
assert vectors.shape[0] >= 60,        f"❌ Expected ≥ 60 embeddings, got {vectors.shape[0]}"
print(f"✅ Eval-3.1 PASSED — Embeddings shape: {vectors.shape}")
```

| Check | Pass Condition |
|---|---|
| Array is 2-dimensional | `ndim == 2` |
| Exactly 768 dimensions | `shape[1] == 768` |
| Row count matches chunk count | `shape[0] == len(chunks)` |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-3.2 — Embeddings Are L2-Normalised

```python
norms = np.linalg.norm(vectors, axis=1)
assert np.allclose(norms, 1.0, atol=1e-5), \
    f"❌ Vectors are not L2-normalised. Min norm: {norms.min():.4f}, Max: {norms.max():.4f}"
print("✅ Eval-3.2 PASSED — All vectors are L2-normalised (norm ≈ 1.0)")
```

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-3.3 — Semantic Similarity Sanity Check

```python
from src.ingestion.embedder import Embedder
import numpy as np

embedder = Embedder()

# Similar queries should have high cosine similarity
q1 = embedder.embed_query("What is the expense ratio of HDFC Mid Cap Fund?")
q2 = embedder.embed_query("How much does HDFC Mid Cap charge as expense ratio?")
q3 = embedder.embed_query("What is the minimum SIP amount for Union Liquid Fund?")

sim_similar   = float(np.dot(q1, q2))   # Should be HIGH (same meaning)
sim_dissimilar = float(np.dot(q1, q3))  # Should be LOWER (different meaning)

assert sim_similar > 0.80,    f"❌ Similar queries similarity too low: {sim_similar:.3f}"
assert sim_dissimilar < sim_similar, \
    f"❌ Dissimilar query scored higher than similar: {sim_dissimilar:.3f} > {sim_similar:.3f}"
print(f"✅ Eval-3.3 PASSED — Similar: {sim_similar:.3f}, Dissimilar: {sim_dissimilar:.3f}")
```

| Check | Pass Condition |
|---|---|
| Similar queries cosine similarity | > `0.80` |
| Dissimilar queries score lower | `sim_dissimilar < sim_similar` |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-3.4 — `embed_query()` and `embed_documents()` Output Shape

```python
q_vec   = embedder.embed_query("test query")
doc_vec = embedder.embed_documents(["doc one", "doc two"])

assert q_vec.shape   == (768,),    f"❌ embed_query shape: {q_vec.shape}"
assert doc_vec.shape == (2, 768),  f"❌ embed_documents shape: {doc_vec.shape}"
print("✅ Eval-3.4 PASSED — embed_query: (768,) | embed_documents: (2, 768)")
```

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Phase 3 Evaluation Summary

| Eval ID | Description | Result |
|---|---|---|
| Eval-3.1 | Embedding shape `(N, 768)` | ☐ |
| Eval-3.2 | All vectors L2-normalised | ☐ |
| Eval-3.3 | Semantic similarity sanity check | ☐ |
| Eval-3.4 | `embed_query` / `embed_documents` output shapes | ☐ |

> **Phase 3 Gate**: All 4 checks must pass before proceeding to Phase 4.

---

## Phase 4 — Vector Store Indexing

**Goal**: Confirm the FAISS index is built, persisted, and can retrieve relevant results.

---

### Eval-4.1 — Index Files Exist

```python
import os
assert os.path.isfile("data/vector_store/index.faiss"), "❌ index.faiss not found"
assert os.path.isfile("data/vector_store/metadata.pkl"), "❌ metadata.pkl not found"
print("✅ Eval-4.1 PASSED — index.faiss and metadata.pkl both exist")
```

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-4.2 — Index Dimension and Vector Count

```python
from src.ingestion.indexer import FAISSIndexer

indexer = FAISSIndexer.load("data/vector_store")
assert indexer.index.d == 768,      f"❌ Index dim is {indexer.index.d}, expected 768"
assert indexer.index.ntotal >= 60,  f"❌ Index has {indexer.index.ntotal} vectors, expected ≥ 60"
assert len(indexer.metadata) == indexer.index.ntotal, \
    f"❌ Metadata count ({len(indexer.metadata)}) ≠ index vector count ({indexer.index.ntotal})"
print(f"✅ Eval-4.2 PASSED — {indexer.index.ntotal} vectors @ dim=768 | metadata synced")
```

| Check | Pass Condition |
|---|---|
| Index dimension | `d == 768` |
| Vector count | `ntotal >= 60` |
| Metadata count matches index | `len(metadata) == ntotal` |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-4.3 — Search Returns Correct Top Result

```python
from src.ingestion.embedder import Embedder
import numpy as np

embedder = Embedder()
test_cases = [
    ("expense ratio of HDFC Mid Cap Fund", "HDFC Mid Cap Fund"),
    ("exit load Union Liquid Fund", "Union Liquid Fund"),
    ("minimum SIP HDFC Small Cap", "HDFC Small Cap Fund"),
    ("riskometer Union Midcap Fund", "Union Midcap Fund"),
]

for query, expected_fund in test_cases:
    q_vec   = embedder.embed_query(query)
    results = indexer.search(q_vec, top_k=3, threshold=0.0)  # threshold=0 to see all
    assert len(results) > 0, f"❌ No results for: {query}"
    top_fund = results[0]["fund_name"]
    assert expected_fund.lower() in top_fund.lower(), \
        f"❌ Top result for '{query}' is '{top_fund}', expected '{expected_fund}'"
    print(f"✅ [{results[0]['score']:.3f}] '{query}' → {top_fund}")
```

| Check | Pass Condition |
|---|---|
| Search returns ≥ 1 result for all 4 queries | `len(results) > 0` |
| Top result fund name matches expected | Expected fund name in `results[0]["fund_name"]` |
| Scores are cosine values (0.0–1.0) | `0.0 ≤ score ≤ 1.0` |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-4.4 — Threshold Filtering Works

```python
q_vec = embedder.embed_query("completely unrelated query about cooking recipes")
results_high_threshold = indexer.search(q_vec, top_k=3, threshold=0.5)
# Should return very few or no results for a completely off-topic query
print(f"✅ Eval-4.4 — Off-topic query returned {len(results_high_threshold)} result(s) above 0.5 threshold")
# Not a hard assertion — just document the behaviour
```

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-4.5 — Index Reload Produces Identical Results

```python
indexer_reloaded = FAISSIndexer.load("data/vector_store")
q_vec = embedder.embed_query("expense ratio HDFC Mid Cap")
r1 = indexer.search(q_vec, top_k=1)
r2 = indexer_reloaded.search(q_vec, top_k=1)
assert r1[0]["chunk_id"] == r2[0]["chunk_id"], "❌ Reload returned different top result"
assert abs(r1[0]["score"] - r2[0]["score"]) < 1e-5, "❌ Reload returned different score"
print("✅ Eval-4.5 PASSED — Reloaded index returns identical results")
```

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Phase 4 Evaluation Summary

| Eval ID | Description | Result |
|---|---|---|
| Eval-4.1 | Both index files exist | ☐ |
| Eval-4.2 | Dim=768, ntotal≥60, metadata synced | ☐ |
| Eval-4.3 | Top result matches expected fund for 4 queries | ☐ |
| Eval-4.4 | Off-topic query filtered by threshold | ☐ |
| Eval-4.5 | Reload returns identical results | ☐ |

> **Phase 4 Gate**: All 5 checks must pass before proceeding to Phase 5.

---

## Phase 5 — Query Classifier

**Goal**: Confirm the rule-based classifier and LLM fallback correctly label factual vs. advisory queries.

---

### Eval-5.1 — Factual Query Classification

```python
from src.retrieval.classifier import classify_query

factual_cases = [
    "What is the expense ratio of HDFC Mid Cap Fund?",
    "What is the exit load for Union Flexi Cap Fund?",
    "What is the minimum SIP amount for HDFC Small Cap?",
    "What is the riskometer of Union Midcap Fund?",
    "How to download capital gains statement?",
    "What is the NAV of HDFC Balanced Advantage Fund?",
    "What is the benchmark index of Union Multicap Fund?",
    "What is the lock-in period of Union Children's Fund?",
]

failures = []
for query in factual_cases:
    result = classify_query(query)
    if result not in ("FACTUAL", "AMBIGUOUS"):  # AMBIGUOUS will go to LLM fallback — acceptable
        failures.append({"query": query, "got": result})

assert len(failures) == 0, f"❌ Factual queries misclassified as ADVISORY: {failures}"
print(f"✅ Eval-5.1 PASSED — {len(factual_cases)} factual queries correctly classified")
```

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-5.2 — Advisory Query Classification

```python
advisory_cases = [
    "Should I invest in HDFC Mid Cap Fund?",
    "Which fund is better — Union or HDFC?",
    "Will this fund give 15% returns?",
    "Recommend a good mutual fund for me",
    "Is HDFC Mid Cap safe for me?",
    "Which is the best mutual fund right now?",
    "Compare Union Midcap and HDFC Mid Cap",
    "Will Union Gold ETF outperform HDFC Gold ETF?",
]

failures = []
for query in advisory_cases:
    result = classify_query(query)
    if result != "ADVISORY":
        failures.append({"query": query, "got": result})

assert len(failures) == 0, f"❌ Advisory queries NOT classified as ADVISORY: {failures}"
print(f"✅ Eval-5.2 PASSED — {len(advisory_cases)} advisory queries correctly classified")
```

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-5.3 — Edge Input Classification

```python
edge_cases = [
    ("", "AMBIGUOUS"),              # empty string → safe default
    ("NAV", "FACTUAL"),             # single keyword
    ("ok", "AMBIGUOUS"),            # meaningless query
]

for query, expected_bucket in edge_cases:
    result = classify_query(query)
    # We don't assert exact match for edge cases — just document actual behaviour
    print(f"  '{query}' → {result}  (expected bucket: {expected_bucket})")

print("✅ Eval-5.3 — Edge input classification documented (no hard assertion)")
```

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-5.4 — LLM Fallback Returns Valid Label

```python
from src.generation.llm import LLMClient
from src.retrieval.classifier import classify_with_llm

llm = LLMClient()

ambiguous_cases = [
    "Tell me about HDFC Mid Cap",
    "What are the details of Union Liquid Fund?",
]

for query in ambiguous_cases:
    result = classify_with_llm(query, llm)
    assert result in ("FACTUAL", "ADVISORY"), \
        f"❌ LLM classifier returned unexpected value '{result}' for: '{query}'"
    print(f"  LLM classified '{query}' → {result}")

print("✅ Eval-5.4 PASSED — LLM fallback always returns FACTUAL or ADVISORY")
```

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Phase 5 Evaluation Summary

| Eval ID | Description | Pass Threshold | Result |
|---|---|---|---|
| Eval-5.1 | Factual queries correctly classified | 8/8 (100%) | ☐ |
| Eval-5.2 | Advisory queries correctly classified | 8/8 (100%) | ☐ |
| Eval-5.3 | Edge inputs documented | N/A (observation) | ☐ |
| Eval-5.4 | LLM fallback returns valid label | 2/2 (100%) | ☐ |

> **Phase 5 Gate**: Eval-5.1 and Eval-5.2 must both be 100%. Eval-5.4 must pass before proceeding to Phase 6.

---

## Phase 6 — Retrieval Engine

**Goal**: Confirm the retriever correctly embeds queries, searches the index, and returns relevant chunks.

---

### Eval-6.1 — Retriever Returns Results for Known Queries

```python
from src.retrieval.retriever import Retriever

r = Retriever()

factual_queries = [
    ("What is the expense ratio of HDFC Mid Cap Fund?",       "HDFC Mid Cap Fund"),
    ("What is the exit load for Union Flexi Cap Fund?",        "Union Flexi Cap Fund"),
    ("What is the minimum SIP for HDFC Small Cap Fund?",       "HDFC Small Cap Fund"),
    ("What is the riskometer rating of Union Midcap Fund?",    "Union Midcap Fund"),
    ("What is the benchmark index of Union Multicap Fund?",    "Union Multicap Fund"),
    ("What is the NAV of HDFC Balanced Advantage Fund?",       "HDFC Balanced Advantage Fund"),
]

failures = []
for query, expected_fund in factual_queries:
    results = r.retrieve(query)
    if not results:
        failures.append({"query": query, "issue": "no results returned"})
        continue
    top_fund = results[0]["fund_name"]
    if expected_fund.lower() not in top_fund.lower():
        failures.append({"query": query, "expected": expected_fund, "got": top_fund})
    print(f"  [{results[0]['score']:.3f}] {query[:50]}... → {top_fund}")

assert len(failures) == 0, f"❌ Retrieval failures: {failures}"
print(f"✅ Eval-6.1 PASSED — {len(factual_queries)}/{len(factual_queries)} queries returned correct top result")
```

| Check | Pass Condition |
|---|---|
| All 6 queries return ≥ 1 result | `len(results) > 0` for all |
| Top result fund name matches expected | 6/6 correct |
| All results have `score ≥ 0.5` | Threshold respected |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-6.2 — Out-of-Corpus Query Returns Empty or Low-Score Results

```python
out_of_scope = [
    "What is the expense ratio of Axis Bluechip Fund?",
    "Tell me about Mirae Asset Emerging Bluechip Fund",
]

for query in out_of_scope:
    results = r.retrieve(query)
    if results:
        print(f"  ⚠️  Out-of-scope query returned {len(results)} result(s) — top score: {results[0]['score']:.3f}")
    else:
        print(f"  ✅  Out-of-scope query correctly returned 0 results: '{query}'")

print("✅ Eval-6.2 — Out-of-corpus behaviour documented")
```

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-6.3 — Result Metadata Is Complete

```python
results = r.retrieve("What is the expense ratio of HDFC Mid Cap Fund?")
assert len(results) > 0

required_keys = ["text", "source_url", "fund_name", "amc", "scraped_date", "score"]
for key in required_keys:
    assert key in results[0], f"❌ Key '{key}' missing from retrieval result"
    assert results[0][key],   f"❌ Key '{key}' is empty in retrieval result"

assert results[0]["source_url"].startswith("https://groww.in/"), \
    f"❌ source_url is not a Groww URL: {results[0]['source_url']}"
print("✅ Eval-6.3 PASSED — All metadata keys present and non-empty")
```

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Phase 6 Evaluation Summary

| Eval ID | Description | Pass Threshold | Result |
|---|---|---|---|
| Eval-6.1 | Correct top result for 6 known queries | 6/6 (100%) | ☐ |
| Eval-6.2 | Out-of-corpus query behaviour documented | Observation | ☐ |
| Eval-6.3 | Retrieval result metadata complete | All keys present | ☐ |

> **Phase 6 Gate**: Eval-6.1 must be 6/6 and Eval-6.3 must pass before proceeding to Phase 7.

---

## Phase 7 — LLM Response Generation

**Goal**: Confirm the LLM generates factual, grounded, correctly formatted responses and refuses advisory queries.

---

### Eval-7.1 — Response Format Contract

For each factual test query, the generated response must conform to:
- ≤ 3 sentences in the factual answer body
- Exactly 1 source URL (injected by `response_builder`)
- A `Last updated from sources: DD-MMM-YYYY` line

```python
from src.generation.response_builder import ResponseBuilder

builder = ResponseBuilder()
result = builder.answer("What is the expense ratio of HDFC Mid Cap Fund?")

response_text = result["response"]
source_url    = result["source_url"]
scraped_date  = result["scraped_date"]

sentence_count = len([s for s in response_text.split(".") if s.strip()])
assert sentence_count <= 3,  f"❌ Response has {sentence_count} sentences (max 3)"
assert source_url is not None, "❌ source_url is None for a factual query"
assert source_url.startswith("https://groww.in/"), f"❌ Invalid source URL: {source_url}"
assert scraped_date is not None, "❌ scraped_date is None for a factual query"
assert result["is_refusal"] == False, "❌ Factual query incorrectly marked as refusal"
print(f"✅ Eval-7.1 PASSED — {sentence_count} sentence(s), source URL present, date present")
```

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-7.2 — Factual Test Suite (6 Queries)

```python
factual_test_cases = [
    ("What is the expense ratio of HDFC Mid Cap Fund?",     ["expense ratio", "hdfc mid cap"]),
    ("What is the exit load for Union Flexi Cap Fund?",      ["exit load", "union"]),
    ("What is the minimum SIP for HDFC Small Cap Fund?",     ["sip", "hdfc small cap"]),
    ("What is the riskometer of Union Midcap Fund?",         ["riskometer", "union midcap"]),
    ("What is the benchmark index of Union Multicap Fund?",  ["benchmark", "union multicap"]),
    ("What is the NAV of HDFC Balanced Advantage Fund?",     ["nav", "hdfc balanced"]),
]

for query, expected_phrases in factual_test_cases:
    result = builder.answer(query)
    resp_lower = result["response"].lower()
    missing = [p for p in expected_phrases if p not in resp_lower]
    if missing:
        print(f"  ⚠️  '{query}' — missing phrases: {missing}")
    else:
        print(f"  ✅  '{query}' — all expected phrases found")
    assert result["source_url"] is not None,   f"❌ No source URL for: {query}"
    assert result["is_refusal"] == False,       f"❌ Wrongly refused: {query}"
```

| Metric | Target |
|---|---|
| Factual queries answered (not refused) | 6/6 |
| Expected fund-specific phrases in response | ≥ 1 of 2 per query |
| Source URL present for all factual answers | 6/6 |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-7.3 — Advisory Query Refusal (No LLM Call)

```python
advisory_cases = [
    "Should I invest in HDFC Mid Cap Fund?",
    "Which fund is better — Union or HDFC?",
    "Will this fund give 20% returns?",
]

refusal_phrases = ["cannot provide", "no investment advice", "facts-only"]

for query in advisory_cases:
    result = builder.answer(query)
    assert result["is_refusal"] == True,      f"❌ Advisory query not marked as refusal: {query}"
    assert result["source_url"] is None,       f"❌ source_url should be None for refusal"
    resp_lower = result["response"].lower()
    has_refusal_phrase = any(p in resp_lower for p in refusal_phrases)
    assert has_refusal_phrase, f"❌ Refusal template not found in response for: {query}"
    print(f"  ✅  Advisory refusal correct: '{query}'")
```

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-7.4 — No Investment Advice in Any Factual Response

**Method**: Manual review of all 6 factual responses

Check each response does not contain:
- `"you should"`, `"I recommend"`, `"better than"`, `"you must"`, `"invest in"`
- Any comparison between two funds
- Any return prediction or safety rating for a user

| Check | Pass Condition |
|---|---|
| No advisory phrasing in any factual response | 0 advisory phrases detected |
| No fund comparison in any response | Manually verified |
| No return prediction in any response | Manually verified |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-7.5 — LLM Provider Fallback

```python
import os
# Temporarily test with Groq fallback
os.environ["LLM_PROVIDER"] = "groq"
builder_groq = ResponseBuilder()
result_groq  = builder_groq.answer("What is the expense ratio of HDFC Mid Cap Fund?")
assert result_groq["is_refusal"] == False
assert result_groq["source_url"] is not None
print(f"✅ Eval-7.5 PASSED — Groq fallback works: {result_groq['response'][:80]}...")
os.environ["LLM_PROVIDER"] = "gemini"  # reset
```

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Phase 7 Evaluation Summary

| Eval ID | Description | Pass Threshold | Result |
|---|---|---|---|
| Eval-7.1 | Response format contract (1 query) | All 3 format checks pass | ☐ |
| Eval-7.2 | Factual test suite | 6/6 answered, not refused | ☐ |
| Eval-7.3 | Advisory refusal (3 queries) | 3/3 correctly refused | ☐ |
| Eval-7.4 | No investment advice in factual responses | Manual review: 0 violations | ☐ |
| Eval-7.5 | Groq fallback provider works | 1/1 response returned | ☐ |

> **Phase 7 Gate**: All 5 checks must pass before proceeding to Phase 8.

---

## Phase 8 — User Interface

**Goal**: Confirm the Streamlit UI launches, renders correctly, and integrates with the full pipeline.

---

### Eval-8.1 — App Launches Without Error

```bash
# Launch the app
streamlit run src/app/main.py &
sleep 5
# Check it is running
curl -s http://localhost:8501 | grep -q "Groww" && echo "✅ UI is running" || echo "❌ UI did not start"
```

| Check | Pass Condition |
|---|---|
| App starts without Python exception | No traceback in terminal |
| App accessible at `localhost:8501` | HTTP 200 response |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-8.2 — UI Component Checklist (Manual)

Open `http://localhost:8501` in a browser and verify:

| Component | Expected | Verified |
|---|---|---|
| Disclaimer banner | Visible at top of page | ☐ |
| Page title | "Groww Mutual Fund FAQ Assistant" | ☐ |
| Welcome expander | Shows 3 example questions | ☐ |
| Chat input box | Present and accepts text | ☐ |
| Submit button / Enter key | Sends query | ☐ |
| Facts-only note | "No investment advice" visible | ☐ |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-8.3 — Factual Query End-to-End in UI (Manual)

Type: `"What is the expense ratio of HDFC Mid Cap Fund?"`

| Expected Element | Verified |
|---|---|
| User message appears in chat | ☐ |
| Spinner shown during processing | ☐ |
| Factual answer appears (≤ 3 sentences) | ☐ |
| Source URL caption shown (`🔗 Source: https://groww.in/...`) | ☐ |
| Last updated date caption shown (`🗓️ Last updated from sources: ...`) | ☐ |
| No investment advice in response | ☐ |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-8.4 — Advisory Query Refusal in UI (Manual)

Type: `"Should I invest in HDFC Mid Cap Fund?"`

| Expected Element | Verified |
|---|---|
| Refusal message appears | ☐ |
| "cannot provide" or "facts-only" phrasing visible | ☐ |
| No source URL caption shown | ☐ |
| No last updated date shown | ☐ |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-8.5 — Chat History Persists Within Session (Manual)

Ask 2 questions in sequence and verify both appear in the chat history.

| Check | Verified |
|---|---|
| First question and answer visible after sending second question | ☐ |
| Messages do not disappear on re-render | ☐ |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Phase 8 Evaluation Summary

| Eval ID | Description | Type | Result |
|---|---|---|---|
| Eval-8.1 | App launches at localhost:8501 | Automated | ☐ |
| Eval-8.2 | All UI components rendered | Manual | ☐ |
| Eval-8.3 | Factual query response in UI | Manual | ☐ |
| Eval-8.4 | Advisory refusal in UI | Manual | ☐ |
| Eval-8.5 | Chat history persists in session | Manual | ☐ |

> **Phase 8 Gate**: Eval-8.1 must pass (automated). Eval-8.2 through 8.5 are manual checks — all must be verified before proceeding to Phase 9.

---

## Phase 9 — Integration & End-to-End Testing

**Goal**: Run the full pipeline test suite covering all 7 defined test cases and validate all success criteria.

---

### Eval-9.1 — Full E2E Test Suite (7 Cases)

```bash
python tests/test_e2e.py
```

Expected output:

```
PASS [FACTUAL]: What is the expense ratio of HDFC Mid Cap Fund?...
PASS [FACTUAL]: What is the exit load for Union Flexi Cap Fund?...
PASS [FACTUAL]: What is the minimum SIP for HDFC Small Cap Fund?...
PASS [FACTUAL]: What is the riskometer rating of Union Midcap Fund?...
PASS [ADVISORY]: Should I invest in HDFC Mid Cap Fund?...
PASS [ADVISORY]: Which fund is better — Union or HDFC?...
PASS [ADVISORY]: Will this fund give 20% returns?...

All E2E tests passed.
```

| Check | Pass Condition |
|---|---|
| All 7 test cases pass | Exit code 0, "All E2E tests passed." printed |
| 4 factual responses have `source_url` | Not `None` |
| 4 factual responses have `scraped_date` | Not `None` |
| 3 advisory responses have `is_refusal=True` | Verified |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-9.2 — Response Quality Metrics

For each of the 4 factual E2E responses:

```python
from src.generation.response_builder import ResponseBuilder
builder = ResponseBuilder()

factual_cases = [
    "What is the expense ratio of HDFC Mid Cap Fund?",
    "What is the exit load for Union Flexi Cap Fund?",
    "What is the minimum SIP for HDFC Small Cap Fund?",
    "What is the riskometer rating of Union Midcap Fund?",
]

import re
date_regex = re.compile(r"\d{2}-[A-Z][a-z]{2}-\d{4}")

for query in factual_cases:
    result   = builder.answer(query)
    response = result["response"]
    sentences = [s.strip() for s in response.split(".") if s.strip()]

    assert len(sentences) <= 3,                f"❌ Too many sentences ({len(sentences)}) for: {query}"
    assert result["source_url"] is not None,   f"❌ No source URL for: {query}"
    assert result["source_url"].startswith("https://groww.in/"), f"❌ Invalid URL"
    assert date_regex.search(result["scraped_date"] or ""), f"❌ Invalid date format"
    print(f"  ✅  {len(sentences)} sentence(s) | URL: ...{result['source_url'][-30:]} | Date: {result['scraped_date']}")
```

| Metric | Target |
|---|---|
| Answer ≤ 3 sentences | 4/4 |
| Exactly 1 source URL (from chunk metadata) | 4/4 |
| Date in `DD-MMM-YYYY` format | 4/4 |
| No investment advice phrases | 4/4 (manual) |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-9.3 — Privacy Audit

```bash
grep -rE "[A-Z]{5}[0-9]{4}[A-Z]|[0-9]{12}|[6-9][0-9]{9}" data/
echo "Exit code: $? (0 = no matches found = PASS)"
```

| Check | Pass Condition |
|---|---|
| PAN pattern matches | 0 |
| Aadhaar pattern matches | 0 |
| Phone number pattern matches | 0 |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-9.4 — Classifier Unit Tests

```bash
python tests/test_classifier.py
```

Expected: `All classifier tests passed.`

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Phase 9 Evaluation Summary

| Eval ID | Description | Pass Threshold | Result |
|---|---|---|---|
| Eval-9.1 | Full E2E suite (7 cases) | 7/7 (100%) | ☐ |
| Eval-9.2 | Response quality metrics | 4/4 factual cases | ☐ |
| Eval-9.3 | Privacy / PII audit | 0 matches | ☐ |
| Eval-9.4 | Classifier unit tests | All assertions pass | ☐ |

> **Phase 9 Gate**: All 4 checks must pass (100%) before proceeding to Phase 10.

---

## Phase 10 — Final Polish & Documentation

**Goal**: Confirm the README is complete, all error scenarios are handled, and the project is ready for handoff.

---

### Eval-10.1 — README Completeness

Open `README.md` and verify all 6 required sections are present:

| Section | Present |
|---|---|
| Project overview and disclaimer | ☐ |
| Selected AMCs and all 20 fund URLs | ☐ |
| Architecture overview (link to `architecture.md`) | ☐ |
| Prerequisites (Python 3.10+, API key setup) | ☐ |
| Build index instructions (`python scripts/build_index.py`) | ☐ |
| Run app instructions (`streamlit run src/app/main.py`) | ☐ |
| Known limitations section | ☐ |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-10.2 — Error Handling Spot-Check

| Scenario | Test Method | Expected |
|---|---|---|
| Missing API key | Unset `GEMINI_API_KEY` in `.env`; run a factual query | Fallback message returned, no crash |
| Index not found | Delete `data/vector_store/`; start UI | Clear error message shown, not a Python traceback |
| Empty query | Submit empty string via UI | Prompt shown, not processed |
| Advisory query | Submit `"Should I invest?"` | Refusal template shown, no source URL |
| LLM rate limit | Exhaust Gemini quota; query with `LLM_PROVIDER=gemini` | Auto-switches to Groq or returns fallback |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-10.3 — `.gitignore` Audit

```bash
cat .gitignore
```

| Required Entry | Present |
|---|---|
| `.env` | ☐ |
| `data/raw/` | ☐ |
| `data/chunks/` | ☐ |
| `data/vector_store/` | ☐ |
| `venv/` or `.venv/` | ☐ |
| `__pycache__/` | ☐ |
| `*.pyc` | ☐ |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Eval-10.4 — Final Success Criteria Checklist (from `context.md §11`)

| Criterion | Verification | Status |
|---|---|---|
| ✅ Retrieval Accuracy | E2E test: top result fund matches query fund | ☐ |
| ✅ Response Compliance | Manual: ≤ 3 sentences, 1 citation, date present | ☐ |
| ✅ Refusal Accuracy | E2E test: all 3 advisory queries return refusal | ☐ |
| ✅ Privacy Safety | PII grep returns 0 matches in `data/` | ☐ |
| ✅ UI Quality | Manual: disclaimer visible, example questions shown, chat works | ☐ |
| ✅ Source Traceability | Every factual response has a valid `groww.in` URL | ☐ |

**Status**: ☐ Pass &nbsp; ☐ Fail

---

### Phase 10 Evaluation Summary

| Eval ID | Description | Result |
|---|---|---|
| Eval-10.1 | README has all 7 required sections | ☐ |
| Eval-10.2 | All 5 error scenarios handled gracefully | ☐ |
| Eval-10.3 | `.gitignore` covers all sensitive paths | ☐ |
| Eval-10.4 | All 6 success criteria met | ☐ |

---

## Overall Evaluation Scorecard

| Phase | Eval Count | Pass Condition |
|---|---|---|
| **Phase 0** — Environment Setup | 4 | 4/4 |
| **Phase 1** — Data Scraping | 4 | 4/4 |
| **Phase 2** — Text Chunking | 4 | 4/4 |
| **Phase 3** — Embedding | 4 | 4/4 |
| **Phase 4** — Vector Store | 5 | 5/5 |
| **Phase 5** — Query Classifier | 4 | Eval-5.1, 5.2, 5.4 must pass (100%) |
| **Phase 6** — Retrieval Engine | 3 | Eval-6.1: 6/6, Eval-6.3 must pass |
| **Phase 7** — LLM Generation | 5 | 5/5 |
| **Phase 8** — User Interface | 5 | 5/5 (1 automated + 4 manual) |
| **Phase 9** — Integration Testing | 4 | 4/4 (100%) |
| **Phase 10** — Polish & Docs | 4 | 4/4 |
| **TOTAL** | **46** | **All 46 evals must pass** |

---

### How to Use This Document

1. **Run in order** — each phase gate must be satisfied before progressing to the next phase.
2. **Mark results** — update each `☐ Pass / ☐ Fail` cell as evaluations are completed.
3. **On failure** — refer to [edge-cases.md](./edge-cases.md) for the relevant edge case (EC-*) and its prescribed mitigation.
4. **Re-evaluate** — after fixing a failure, re-run only the affected phase's evaluations, then continue.

---

*Evaluation Guide for: Groww Mutual Fund FAQ RAG Chatbot*
*Generated from: [implementationplan.md](./implementationplan.md) | [architecture.md](./architecture.md)*
*Total Evaluations: 46 across 11 phases | Last updated: 2026-06-30*
