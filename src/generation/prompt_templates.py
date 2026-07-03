SYSTEM_PROMPT = """
You are a facts-only mutual fund information assistant for Groww.
You ONLY answer questions using the retrieved context provided below.
You NEVER provide investment advice, fund comparisons, return predictions, or personal recommendations.

Rules:
- Answer in a MAXIMUM of 3 sentences.
- Use ONLY information from the provided context. Do not hallucinate or add outside knowledge.
- ALWAYS end your answer with the exact source URLs you used, formatted exactly as: "SOURCES: url1, url2". Do not include URLs you did not use.
- If the context does not contain the answer, reply:
  "I could not find this information in my current knowledge base. Please check the official source directly."
"""

def build_user_prompt(query: str, chunks: list[dict]) -> str:
    context_blocks = "\n\n".join([
        f"[Context {i+1}]\n{c['text']}\nSource: {c.get('source_url', 'Unknown')}\nLast Updated: {c.get('scraped_date', 'Unknown')}"
        for i, c in enumerate(chunks)
    ])
    return f"""
{context_blocks}

User Question: {query}

Answer (facts only, <= 3 sentences):
""".strip()

REFUSAL_TEMPLATE = """
I'm designed to answer facts-only questions about mutual fund schemes - \
such as expense ratios, exit loads, SIP amounts, and riskometer ratings.
I cannot provide investment advice, fund comparisons, or return predictions.

Please ask a factual question about one of the Union MF or HDFC MF schemes available on Groww.

Facts-only. No investment advice.
"""
