import json

with open("data/chunks/chunks.json", encoding="utf-8") as f:
    chunks = json.load(f)

required = ["chunk_id", "text", "source_url", "fund_name", "amc", "scraped_date"]
for c in chunks:
    missing = [k for k in required if not c.get(k)]
    if missing:
        print(f"WARN: {c['chunk_id']} missing: {missing}")

print(f"Total chunks: {len(chunks)}")
print(f"Funds covered: {len(set(c['fund_name'] for c in chunks))}")
