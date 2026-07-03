from src.ingestion.embedder import Embedder   # uses BAAI/bge-small-en-v1.5
from src.ingestion.indexer import FAISSIndexer

class Retriever:
    def __init__(self, index_path: str = "data/vector_store", top_k: int = 10, threshold: float = 0.5):
        self.embedder = Embedder()
        self.indexer  = FAISSIndexer.load(index_path)
        self.top_k    = top_k
        self.threshold = threshold

    def retrieve(self, query: str) -> list[dict]:
        """
        Returns a list of top-k relevant chunks with metadata.
        Each result: {text, source_url, fund_name, amc, scraped_date, score}
        """
        query_vec = self.embedder.embed_query(query)
        results   = self.indexer.search(query_vec, top_k=self.top_k, threshold=self.threshold)

        if not results:
            return []  # triggers "not found" response in generator

        return results
