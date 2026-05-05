import os
import httpx
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
    """
    Generates 384-dimensional text embeddings via Google Gemini REST API.
    Calls the API directly with httpx (no SDK version dependency).
    Tries multiple models/versions until one works.
    """

    EMBEDDING_DIM = 384
    BASE_URL = "https://generativelanguage.googleapis.com/{version}/models/{model}:embedContent"

    MODELS_TO_TRY = [
        ("v1beta", "text-embedding-004"),
        ("v1",     "text-embedding-004"),
        ("v1beta", "gemini-embedding-exp-03-07"),
        ("v1beta", "embedding-001"),
        ("v1",     "embedding-001"),
    ]

    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.working_model = None
        if self.gemini_key:
            print(f"EmbeddingService: Gemini key loaded (last 6 chars: ...{self.gemini_key[-6:]}).")
        else:
            print("EmbeddingService: WARNING - No GEMINI_API_KEY found!")

    def embed(self, text: str) -> list:
        """Returns a 384-dimensional embedding vector for the given text."""
        if not self.gemini_key:
            raise RuntimeError("GEMINI_API_KEY is not set.")

        if self.working_model:
            version, model = self.working_model
            return self._call(version, model, text)

        last_error = None
        for version, model in self.MODELS_TO_TRY:
            try:
                result = self._call(version, model, text)
                self.working_model = (version, model)
                print(f"EmbeddingService: '{version}/{model}' works!")
                return result
            except Exception as e:
                print(f"EmbeddingService: '{version}/{model}' failed: {str(e)[:120]}")
                last_error = e

        raise RuntimeError(f"All Gemini embedding models failed. Last error: {last_error}")

    def _call(self, version: str, model: str, text: str) -> list:
        url = self.BASE_URL.format(version=version, model=model)
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
        return values[:self.EMBEDDING_DIM]
