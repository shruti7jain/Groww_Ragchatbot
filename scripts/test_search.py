from src.ingestion.indexer import FAISSIndexer
from src.ingestion.embedder import Embedder

print("Loading indexer...")
indexer = FAISSIndexer.load("data/vector_store")

print("Loading embedder...")
embedder = Embedder() # 384-dim

query = "What is the NAV of HDFC Balanced Advantage Fund?"
print(f"Query: '{query}'")

query_vec = embedder.embed_query(query)

print("Searching...")
results = indexer.search(query_vec, top_k=3, threshold=0.3) # BGE cosine scores are often between 0.3 and 1.0

for i, res in enumerate(results):
    print(f"[{i+1}] Score: {res['score']:.4f} | Fund: {res.get('fund_name', 'Unknown')}")
