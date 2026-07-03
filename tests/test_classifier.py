import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.retrieval.classifier import classify_query

print("Running classifier unit tests...")

# Factual queries - must return FACTUAL
assert classify_query("What is the expense ratio of HDFC Mid Cap Fund?") == "FACTUAL"
assert classify_query("What is the exit load for Union Flexi Cap Fund?") == "FACTUAL"
assert classify_query("What is the minimum SIP amount for HDFC Small Cap?") == "FACTUAL"
assert classify_query("What is the riskometer of Union Midcap Fund?") == "FACTUAL"
assert classify_query("How to download capital gains statement?") == "FACTUAL"

# Advisory queries - must return ADVISORY
assert classify_query("Should I invest in HDFC Mid Cap Fund?") == "ADVISORY"
assert classify_query("Which fund is better - Union or HDFC?") == "ADVISORY"
assert classify_query("Will this fund give 15% returns?") == "ADVISORY"
assert classify_query("Recommend a good mutual fund for me") == "ADVISORY"

# Ambiguous queries
assert classify_query("Tell me about something completely random") == "AMBIGUOUS"

print("All classifier tests passed successfully!")
