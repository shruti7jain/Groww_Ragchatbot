import json, os, glob

required_fields = ["fund_name", "expense_ratio", "exit_load", "riskometer", "source_url"]

for path in glob.glob("data/raw/**/*.json", recursive=True):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    missing = [k for k in required_fields if not data.get(k) or data.get(k) == "N/A"]
    if missing:
        print(f"WARN: {path} missing fields: {missing}")
    else:
        print(f"OK: {path}")
