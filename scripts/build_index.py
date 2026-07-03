import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.scraper.urls import CORPUS_URLS
from src.scraper.scraper import scrape_all
from src.ingestion.chunker import process_all_raw
from src.ingestion.embedder import Embedder
from src.ingestion.indexer import FAISSIndexer
import numpy as np

print("[1/4] Scraping Groww fund pages...")
scrape_all(CORPUS_URLS, output_dir="data/raw")

print("[2/4] Chunking scraped data...")
chunks = process_all_raw("data/raw", "data/chunks")

print("[3/4] Generating BGE embeddings (BAAI/bge-small-en-v1.5)...")
embedder = Embedder()  # 384-dim
texts   = [c["text"] for c in chunks]
vectors = embedder.embed_documents(texts)

print("[4/4] Building FAISS index...")
indexer = FAISSIndexer(dim=384)
indexer.add(np.array(vectors), chunks)
indexer.save("data/vector_store")

print("\nBuild complete. Vector store ready at data/vector_store/")
