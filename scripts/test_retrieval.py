from src.retrieval.retriever import Retriever

r = Retriever()

test_queries = [
    "What is the expense ratio of HDFC Mid Cap Fund?",
    "What is the exit load for Union Flexi Cap Fund?",
    "What is the minimum SIP for HDFC Small Cap Fund?",
    "What is the riskometer rating of Union Midcap Fund?",
]

for q in test_queries:
    print(f"\nQuery: {q}")
    results = r.retrieve(q)
    for res in results:
        print(f"  [{res['score']:.3f}] {res['fund_name']} - {res['text'][:80]}...")
        print(f"  Source: {res['source_url']}")
