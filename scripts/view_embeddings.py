import json
import numpy as np

# Load chunks metadata
with open("data/chunks/chunks.json", encoding="utf-8") as f:
    chunks = json.load(f)

# Load embeddings
vectors = np.load("data/chunks/embeddings.npy")

print(f"Total Chunks: {len(chunks)}")
print(f"Total Embeddings: {vectors.shape[0]}")
print(f"Embedding Dimensions: {vectors.shape[1]}")
print("-" * 50)

# Iterate through and show a preview of each embedding
for i, chunk in enumerate(chunks):
    fund_name = chunk.get("fund_name", "Unknown Fund")
    vector = vectors[i]
    
    # We slice the first 5 dimensions just for visual preview
    vector_preview = [round(float(val), 4) for val in vector[:5]]
    
    print(f"[{i+1}/19] Fund: {fund_name}")
    print(f"         Vector Preview (first 5 dims): {vector_preview} ...")
    print(f"         Vector L2 Norm (should be ~1.0): {round(np.linalg.norm(vector), 4)}")
    print("-" * 50)
