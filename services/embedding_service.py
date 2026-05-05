import os
import httpx
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
    """
    Generates 384-dimensional text embeddings.
    Calls the Google Gemini REST API directly (bypasses SDK version issues).
    Model: text-embedding-004
    """

    EMBEDDING_DIM = 384
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/text-embedding-004:embedContent"

    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        if self.gemini_key:
            print("EmbeddingService: Gemini API key loaded.")
        else:
            print("EmbeddingService: WARNING - No GEMINI_API_KEY found!")

    def embed(self, text: str) -> list:
        """Returns a 384-dimensional embedding vector for the given text."""
        if not self.gemini_key:
            raise RuntimeError("GEMINI_API_KEY is not set. Cannot generate embeddings.")

        payload = {
            "model": "models/text-embedding-004",
            "content": {
                "parts": [{"text": text}]
            },
            "outputDimensionality": self.EMBEDDING_DIM
        }

        with httpx.Client() as client:
            response = client.post(
                self.GEMINI_API_URL,
                params={"key": self.gemini_key},
                json=payload,
                timeout=30.0
            )

        if response.status_code != 200:
            raise RuntimeError(
                f"Gemini embedding API error {response.status_code}: {response.text[:300]}"
            )

        result = response.json()
        return result["embedding"]["values"]

