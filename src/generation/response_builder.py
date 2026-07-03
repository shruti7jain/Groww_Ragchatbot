from src.retrieval.classifier import classify_query, classify_with_llm
from src.retrieval.retriever import Retriever
from src.generation.llm import LLMClient
from src.generation.prompt_templates import SYSTEM_PROMPT, build_user_prompt, REFUSAL_TEMPLATE

class ResponseBuilder:
    def __init__(self):
        self.retriever = Retriever()
        self.llm       = LLMClient()

    def answer(self, query: str) -> dict:
        """
        Returns a dict: {response, source_url, scraped_date, is_refusal}
        """
        # Step 1: Classify
        classification = classify_query(query)
        if classification == "AMBIGUOUS":
            classification = classify_with_llm(query, self.llm)

        if classification == "ADVISORY":
            return {
                "response":     REFUSAL_TEMPLATE,
                "source_url":   None,
                "scraped_date": None,
                "is_refusal":   True,
            }

        # Step 2: Retrieve
        chunks = self.retriever.retrieve(query)
        if not chunks:
            return {
                "response":     "I could not find relevant information in my knowledge base. Please try rephrasing your question or visit the official AMC page.",
                "source_url":   None,
                "scraped_date": None,
                "is_refusal":   False,
            }

        # Step 3: Generate
        user_prompt = build_user_prompt(query, chunks)
        response    = self.llm.generate(SYSTEM_PROMPT, user_prompt)

        # Post-processing: Explicitly remove any "Source:" or "Last Updated:" lines if the LLM appended them
        import re
        response = re.sub(r"(?im)^source:.*$", "", response)
        response = re.sub(r"(?im)^last updated:.*$", "", response)
        response = response.strip()

        sources = []
        seen_urls = set()
        for c in chunks:
            url = c.get("source_url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                sources.append({"url": url, "date": c.get("scraped_date", "Unknown")})

        return {
            "response":     response,
            "sources":      sources,
            "is_refusal":   False,
        }
