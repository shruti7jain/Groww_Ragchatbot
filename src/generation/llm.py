"""
Module for interacting with LLM providers (Google Gemini, Groq).
"""
import os
from dotenv import load_dotenv
import groq
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

load_dotenv()

class LLMClient:
    def __init__(self, provider: str = None):
        self.provider = provider or os.getenv("LLM_PROVIDER", "groq")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if self.provider == "gemini":
            return self._gemini(system_prompt, user_prompt)
        elif self.provider == "groq":
            return self._groq(system_prompt, user_prompt)
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}. Use 'gemini' or 'groq'.")

    def _gemini(self, system_prompt: str, user_prompt: str) -> str:
        """Primary LLM - Google Gemini Flash (free tier)."""
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel(
            "gemini-1.5-flash",
            system_instruction=system_prompt
        )
        response = model.generate_content(user_prompt)
        return response.text

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type(groq.RateLimitError)
    )
    def _groq(self, system_prompt: str, user_prompt: str) -> str:
        """Fallback LLM - Groq (Llama 3.3 70B, free tier, handled rate limits)."""
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0.1,    # low temperature for factual accuracy
            max_tokens=256,     # enforce brevity (<=3 sentences)
        )
        return response.choices[0].message.content
