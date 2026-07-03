import json, numpy as np
from src.ingestion.embedder import Embedder

# Load chunks
with open("data/chunks/chunks.json", encoding="utf-8") as f:
    chunks = json.load(f)

texts = [c["text"] for c in chunks]

# Embed
embedder = Embedder()
vectors = embedder.embed_documents(texts)  # shape: (n_chunks, 384)

# Save embeddings separately for inspection / reuse
np.save("data/chunks/embeddings.npy", vectors)
print(f"Embeddings saved - shape: {vectors.shape}")
