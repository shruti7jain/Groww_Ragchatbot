"""
scripts/eval/eval_phase0.py
Phase 0 Evaluation — run after environment setup is complete.
Usage: python scripts/eval/eval_phase0.py
"""
import os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

PASS = True

def check(label, condition, detail=""):
    global PASS
    status = "✅ PASS" if condition else "❌ FAIL"
    if not condition:
        PASS = False
    print(f"  {status}  {label}" + (f" — {detail}" if detail else ""))
    return condition

print("\n══════════════════════════════════════════════")
print("  Phase 0 Evaluation: Environment Setup")
print("══════════════════════════════════════════════\n")

# ── Eval-0.1: Directory Structure ──────────────────────────────
print("Eval-0.1 — Directory Structure")
required_dirs = [
    "docs", "data/raw/union", "data/raw/hdfc",
    "data/chunks", "data/vector_store",
    "src/scraper", "src/ingestion", "src/retrieval",
    "src/generation", "src/app", "scripts", "tests",
]
for d in required_dirs:
    check(d, os.path.isdir(os.path.join(ROOT, d)))

required_files = ["requirements.txt", ".env.example", ".gitignore", "README.md"]
for f in required_files:
    check(f, os.path.isfile(os.path.join(ROOT, f)))

init_files = [
    "src/__init__.py", "src/scraper/__init__.py",
    "src/ingestion/__init__.py", "src/retrieval/__init__.py",
    "src/generation/__init__.py", "src/app/__init__.py",
    "tests/__init__.py",
]
for f in init_files:
    check(f"__init__.py — {f}", os.path.isfile(os.path.join(ROOT, f)))

# ── Eval-0.2: Dependency Imports ───────────────────────────────
print("\nEval-0.2 — Dependency Imports")
import_checks = [
    ("requests",            "requests"),
    ("beautifulsoup4",      "bs4"),
    ("langchain",           "langchain"),
    ("sentence-transformers","sentence_transformers"),
    ("faiss-cpu",           "faiss"),
    ("streamlit",           "streamlit"),
    ("python-dotenv",       "dotenv"),
    ("tqdm",                "tqdm"),
    ("google-generativeai", "google.generativeai"),
    ("groq",                "groq"),
]
for pkg_name, import_name in import_checks:
    try:
        __import__(import_name)
        check(pkg_name, True)
    except ImportError as e:
        check(pkg_name, False, str(e))

# ── Eval-0.3: .env.example Completeness ────────────────────────
print("\nEval-0.3 — .env.example Keys")
with open(os.path.join(ROOT, ".env.example")) as f:
    env_content = f.read()
required_keys = [
    "GEMINI_API_KEY", "GROQ_API_KEY", "LLM_PROVIDER",
    "TOP_K_RETRIEVAL", "SIMILARITY_THRESHOLD",
    "VECTOR_STORE_TYPE", "EMBEDDING_MODEL",
]
for key in required_keys:
    check(key, key in env_content)
check("EMBEDDING_MODEL=BAAI/bge-base-en-v1.5",
      "EMBEDDING_MODEL=BAAI/bge-base-en-v1.5" in env_content)
check("No real API keys committed",
      "your_gemini_api_key_here" in env_content and "your_groq_api_key_here" in env_content)

# ── Eval-0.4: Corpus URL Registry ──────────────────────────────
print("\nEval-0.4 — Corpus URL Registry")
try:
    from src.scraper.urls import CORPUS_URLS
    all_urls = [u for urls in CORPUS_URLS.values() for u in urls]
    check("Exactly 2 AMC keys",             len(CORPUS_URLS) == 2)
    check("Union Mutual Fund key present",  "Union Mutual Fund" in CORPUS_URLS)
    check("HDFC Mutual Fund key present",   "HDFC Mutual Fund"  in CORPUS_URLS)
    check("Union MF has 10 URLs",           len(CORPUS_URLS["Union Mutual Fund"]) == 10)
    check("HDFC MF has 10 URLs",            len(CORPUS_URLS["HDFC Mutual Fund"])  == 10)
    check("All 20 URLs are unique",         len(set(all_urls)) == 20)
    check("All URLs are Groww MF URLs",
          all(u.startswith("https://groww.in/mutual-funds/") for u in all_urls))
except Exception as e:
    check("CORPUS_URLS importable", False, str(e))

# ── Final Result ────────────────────────────────────────────────
print("\n══════════════════════════════════════════════")
if PASS:
    print("  🎉  Phase 0: ALL CHECKS PASSED — proceed to Phase 1")
else:
    print("  ❌  Phase 0: SOME CHECKS FAILED — review output above")
print("══════════════════════════════════════════════\n")
sys.exit(0 if PASS else 1)
