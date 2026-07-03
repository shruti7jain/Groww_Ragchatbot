"""
Module for generating embeddings using the SentenceTransformer model.
Optimized for BAAI/bge-small-en-v1.5.
"""
from sentence_transformers import SentenceTransformer
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# BGE small model — optimised for retrieval; fast and memory-efficient
MODEL_NAME = "BAAI/bge-small-en-v1.5"  # 384-dim, free, runs locally

# BGE models require this prefix on queries (not on documents)
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

class Embedder:
    """Wrapper class for the embedding model."""
    
    def __init__(self, model_name: str = MODEL_NAME):
        """Initialise the Embedder with a specified model."""
        logging.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        """
        Embed a list of document/chunk texts.
        Returns numpy array of shape (n_texts, 384).
        BGE documents are embedded WITHOUT the query prefix.
        """
        return self.model.encode(
            texts,
            show_progress_bar=True,
            normalize_embeddings=True,  # L2 normalise for cosine similarity
            batch_size=32
        )

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single user query.
        BGE queries REQUIRE the instruction prefix for best retrieval performance.
        """
        prefixed = QUERY_PREFIX + query
        return self.model.encode(
            [prefixed],
            normalize_embeddings=True
        )[0]
