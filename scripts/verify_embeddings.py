import numpy as np

vectors = np.load("data/chunks/embeddings.npy")
assert vectors.ndim == 2,             "Expected 2D array"
assert vectors.shape[1] == 384,       "BGE small produces 384-dim vectors"
assert vectors.shape[0] == 19,        "Expected 19 chunks (one per valid fund)"
print(f"Embedding check passed - {vectors.shape[0]} chunks x {vectors.shape[1]} dims")
