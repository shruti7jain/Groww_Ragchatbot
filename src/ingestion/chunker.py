"""
Module for chunking raw JSON scraped data into text chunks suitable for embedding.
"""
import json, os, glob
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def fund_to_text(fund_data: dict) -> str:
    """Convert a fund JSON record into a natural language paragraph."""
    return f"""
    Fund Name: {fund_data['fund_name']}
    AMC: {fund_data['amc']}
    Category: {fund_data['category']}
    NAV: {fund_data['nav']}
    Expense Ratio: {fund_data['expense_ratio']}
    Exit Load: {fund_data['exit_load']}
    Minimum SIP Amount: {fund_data['min_sip']}
    Riskometer: {fund_data['riskometer']}
    Benchmark Index: {fund_data['benchmark']}
    Lock-in Period: {fund_data['lock_in']}
    Source: {fund_data['source_url']}
    Last Scraped: {fund_data['scraped_date']}
    """.strip()

def process_all_raw(raw_dir: str, chunks_dir: str) -> list[dict]:
    """Load all raw JSONs, convert to chunks, save with metadata."""
    os.makedirs(chunks_dir, exist_ok=True)
    all_chunks = []

    for path in glob.glob(f"{raw_dir}/**/*.json", recursive=True):
        with open(path, encoding="utf-8") as f:
            fund = json.load(f)
        text = fund_to_text(fund)
        # Record-level chunking: 1 chunk = 1 fund
        all_chunks.append({
            "chunk_id":     f"{fund['fund_name'].lower().replace(' ', '_')}_chunk_0",
            "text":         text,
            "source_url":   fund["source_url"],
            "fund_name":    fund["fund_name"],
            "amc":          fund["amc"],
            "scraped_date": fund["scraped_date"],
        })

    output_path = f"{chunks_dir}/chunks.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    logging.info(f"Chunking complete - {len(all_chunks)} chunks saved to {output_path}")
    return all_chunks

if __name__ == "__main__":
    logging.info("Starting chunking process...")
    process_all_raw("data/raw", "data/chunks")
