from src.generation.response_builder import ResponseBuilder
import time

print("Initializing ResponseBuilder...")
builder = ResponseBuilder()

test_queries = [
    "What is the exit load for Union Flexi Cap Fund?",
    "Should I invest in HDFC Mid Cap?",
    "What is the minimum SIP for HDFC Small Cap?",
    "Give me advice on saving taxes with mutual funds.",
]

for q in test_queries:
    print(f"\n==========================================")
    print(f"Query: {q}")
    start_time = time.time()
    
    # Generate the response
    result = builder.answer(q)
    
    elapsed = time.time() - start_time
    
    print(f"Response: {result['response']}")
    if result.get("source_url"):
        print(f"Source: {result['source_url']} (Updated: {result['scraped_date']})")
    
    print(f"Time Taken: {elapsed:.2f}s")
