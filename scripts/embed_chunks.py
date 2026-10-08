import json, numpy as np
from src.ingestion.embedder import Embedder

# Load chunks
with open("data/chunks/chunks.json", encoding="utf-8") as f:
    chunks = json.load(f)

texts = [c["text"] for c in chunks]

if not texts:
    print("No chunks found. Creating empty embeddings array and exiting gracefully.")
    np.save("data/chunks/embeddings.npy", np.empty((0, 384)))
    exit(0)

# Embed
embedder = Embedder()
vectors = embedder.embed_documents(texts)  # shape: (n_chunks, 384)

# Save embeddings separately for inspection / reuse
np.save("data/chunks/embeddings.npy", vectors)
print(f"Embeddings saved - shape: {vectors.shape}")
