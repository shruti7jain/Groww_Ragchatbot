"""
Module for classifying user queries as FACTUAL, ADVISORY, or AMBIGUOUS.
"""
ADVISORY_PATTERNS = [
    "should i", "should i invest", "which is better", "which fund",
    "recommend", "best fund", "best option", "suggest", "advise",
    "will it give", "will it grow", "will this fund", "is it safe",
    "compare", " vs ", "versus", "outperform", "returns", "good returns",
    "safe for me", "right for me", "invest in",
]

FACTUAL_PATTERNS = [
    "expense ratio", "exit load", "minimum sip", "min sip",
    "lock-in", "lock in", "riskometer", "risk level",
    "benchmark", "category", "nav", "net asset value",
    "download", "statement", "capital gains", "sip amount",
    "what is", "how much", "how to",
]

def classify_query(query: str) -> str:
    """Returns 'FACTUAL' or 'ADVISORY' or 'AMBIGUOUS'."""
    q = query.lower()

    # Advisory check takes priority
    if any(pattern in q for pattern in ADVISORY_PATTERNS):
        return "ADVISORY"

    # Factual check
    if any(pattern in q for pattern in FACTUAL_PATTERNS):
        return "FACTUAL"

    # Ambiguous - default to LLM classifier fallback
    return "AMBIGUOUS"

def classify_with_llm(query: str, llm_client) -> str:
    """Use LLM to classify ambiguous queries."""
    prompt = f"""
    You are classifying whether a user query is asking for a financial fact
    or financial advice about mutual funds.

    Query: "{query}"

    Reply with exactly one word - either FACTUAL or ADVISORY.
    - FACTUAL: asking for objective data (expense ratio, exit load, NAV, etc.)
    - ADVISORY: asking for recommendations, comparisons, predictions, or opinions.
    """
    try:
        # Assuming llm_client has a generate method, otherwise adjust later
        result = llm_client.generate(prompt).strip().upper()
        return result if result in ("FACTUAL", "ADVISORY") else "ADVISORY"  # safe default
    except Exception:
        # Fail safe
        return "ADVISORY"
