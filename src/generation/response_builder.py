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

        # Extract URLs from the LLM's response
        import re
        urls_in_response = set(re.findall(r"(https://groww\.in[^\s,]+)", response))
        
        # Post-processing: clean up the text by removing the SOURCES line
        response = re.sub(r"(?im)^sources?:.*$", "", response)
        response = re.sub(r"(?im)^last updated:.*$", "", response)
        response = response.strip()

        sources = []
        seen_urls = set()
        
        # Only include chunks whose URL was cited by the LLM (or top 1 if none cited)
        for c in chunks:
            url = c.get("source_url")
            if url and url not in seen_urls:
                if url in urls_in_response or not urls_in_response:
                    seen_urls.add(url)
                    sources.append({"url": url, "date": c.get("scraped_date", "Unknown")})
                    
        # If we had URLs in the response, we only return those. 
        # If the LLM failed to output any URL, we return the top 1 chunk's URL as fallback.
        if not urls_in_response and len(sources) > 0:
            sources = [sources[0]]

        return {
            "response":     response,
            "sources":      sources,
            "is_refusal":   False,
        }
