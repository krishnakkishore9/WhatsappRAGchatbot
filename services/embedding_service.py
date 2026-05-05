import os
import httpx
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
    """
    Generates 384-dimensional text embeddings.
    Tries a chain of Gemini embedding models via REST API until one works.
    Falls back to the older embedding-001 (768 dims, truncated to 384).
    """

    EMBEDDING_DIM = 384
    BASE_URL = "https://generativelanguage.googleapis.com/v1/models/{model}:embedContent"

    # Try these models in order until one works
    MODELS_TO_TRY = [
        "text-embedding-004",
        "gemini-embedding-exp-03-07",
        "embedding-001",
    ]

    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.working_model = None  # Cache the first working model

        if self.gemini_key:
            print("EmbeddingService: Gemini API key loaded. Will auto-discover working model.")
        else:
            print("EmbeddingService: WARNING - No GEMINI_API_KEY found!")

    def embed(self, text: str) -> list:
        """Returns a 384-dimensional embedding vector for the given text."""
        if not self.gemini_key:
            raise RuntimeError("GEMINI_API_KEY is not set. Cannot generate embeddings.")

        # If we already found a working model, use it directly
        if self.working_model:
            return self._call_model(self.working_model, text)

        # Otherwise, try each model in the list until one works
        last_error = None
        for model in self.MODELS_TO_TRY:
            try:
                result = self._call_model(model, text)
                self.working_model = model  # Cache successful model
                print(f"EmbeddingService: Using model '{model}' (auto-discovered).")
                return result
            except Exception as e:
                print(f"EmbeddingService: Model '{model}' failed: {e}")
                last_error = e

        raise RuntimeError(f"All Gemini embedding models failed. Last error: {last_error}")

    def _call_model(self, model: str, text: str) -> list:
        """Calls the Gemini REST API for a specific embedding model."""
        url = self.BASE_URL.format(model=model)

        # text-embedding-004 supports outputDimensionality; others do not
        payload = {
            "model": f"models/{model}",
            "content": {"parts": [{"text": text}]}
        }
        if model == "text-embedding-004":
            payload["outputDimensionality"] = self.EMBEDDING_DIM

        with httpx.Client() as client:
            response = client.post(
                url,
                params={"key": self.gemini_key},
                json=payload,
                timeout=30.0
            )

        if response.status_code != 200:
            raise RuntimeError(f"{response.status_code}: {response.text[:200]}")

        values = response.json()["embedding"]["values"]

        # Truncate to 384 dims for models that output more (e.g. embedding-001 → 768)
        return values[:self.EMBEDDING_DIM]
