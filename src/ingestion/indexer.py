"""
Module for creating, saving, and loading FAISS vector stores.
"""
import faiss
import numpy as np
import pickle, os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class FAISSIndexer:
    """Class to manage the FAISS index and associated metadata."""
    
    def __init__(self, dim: int = 384):  # 384-dim for BAAI/bge-small-en-v1.5
        """Initialize the FAISS index with inner product metric."""
        self.index = faiss.IndexFlatIP(dim)  # Inner Product (cosine on L2-normalised vecs)
        self.metadata = []

    def add(self, vectors: np.ndarray, metadata: list[dict]):
        """Add vectors and their metadata to the index."""
        self.index.add(vectors.astype("float32"))
        self.metadata.extend(metadata)

    def save(self, path: str = "data/vector_store"):
        """Save the FAISS index and metadata to disk."""
        os.makedirs(path, exist_ok=True)
        faiss.write_index(self.index, f"{path}/index.faiss")
        with open(f"{path}/metadata.pkl", "wb") as f:
            pickle.dump(self.metadata, f)
        logging.info(f"Index saved: {self.index.ntotal} vectors @ {self.index.d} dims")

    @classmethod
    def load(cls, path: str = "data/vector_store"):
        obj = cls.__new__(cls)
        obj.index = faiss.read_index(f"{path}/index.faiss")
        with open(f"{path}/metadata.pkl", "rb") as f:
            obj.metadata = pickle.load(f)
        return obj

    def search(self, query_vec: np.ndarray, top_k: int = 3, threshold: float = 0.5):
        scores, indices = self.index.search(query_vec.reshape(1, -1).astype("float32"), top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1 and score >= threshold:
                results.append({**self.metadata[idx], "score": float(score)})
        return results
