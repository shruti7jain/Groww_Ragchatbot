from src.scraper.urls import CORPUS_URLS
from src.scraper.scraper import scrape_all
from src.ingestion.chunker import process_all_raw
from src.ingestion.embedder import Embedder
from src.ingestion.indexer import FAISSIndexer
import numpy as np

# Note: We won't re-run scrape_all here to save time and bandwidth,
# since data is already in data/raw. But normally this script runs the whole pipeline.

print("[1/4] Scraping Groww fund pages... (Skipped, using existing data/raw)")
# scrape_all(CORPUS_URLS, output_dir="data/raw")

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
