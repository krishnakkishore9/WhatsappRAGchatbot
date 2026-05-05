import os
import httpx
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
    """
    Generates 384-dimensional text embeddings with a fallback chain:
    1. Google Gemini text-embedding-004 (free, primary)
    2. HuggingFace all-MiniLM-L6-v2 via Inference API (free, fallback)
    """

    GEMINI_MODEL = "models/text-embedding-004"
    HF_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM = 384

    def __init__(self):
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.hf_key = os.getenv("HF_API_KEY", "").strip()

        if gemini_key:
            try:
                genai.configure(api_key=gemini_key)
                self.gemini_available = True
                print("EmbeddingService: Google Gemini configured.")
            except Exception as e:
                print(f"EmbeddingService: Gemini config failed: {e}")
                self.gemini_available = False
        else:
            self.gemini_available = False
            print("EmbeddingService: No GEMINI_API_KEY found.")

        if self.hf_key:
            print("EmbeddingService: HuggingFace fallback available.")
        else:
            print("EmbeddingService: WARNING - No HF_API_KEY found. Fallback unavailable.")

    def embed(self, text: str) -> list:
        """Returns a 384-dimensional embedding vector for the given text."""
        # 1. Try Google Gemini
        if self.gemini_available:
            try:
                result = genai.embed_content(
                    model=self.GEMINI_MODEL,
                    content=text,
                    output_dimensionality=self.EMBEDDING_DIM
                )
                return result['embedding']
            except Exception as e:
                print(f"EmbeddingService: Gemini failed ({e}), falling back to HuggingFace...")

        # 2. Fallback: HuggingFace Inference API
        return self._embed_huggingface(text)

    def _embed_huggingface(self, text: str) -> list:
        """Calls HuggingFace Inference API for all-MiniLM-L6-v2 (384 dims)."""
        if not self.hf_key:
            raise RuntimeError("No embedding service available. Please set GEMINI_API_KEY or HF_API_KEY.")

        api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.HF_MODEL}"
        headers = {"Authorization": f"Bearer {self.hf_key}"}

        with httpx.Client() as client:
            response = client.post(
                api_url,
                headers=headers,
                json={"inputs": text, "options": {"wait_for_model": True}},
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()

        # HF returns a list of token embeddings; we mean-pool to get sentence embedding
        if isinstance(result[0], list):
            # Token-level embeddings — mean pool across tokens
            tokens = result
            mean_vec = [sum(t[i] for t in tokens) / len(tokens) for i in range(len(tokens[0]))]
            return mean_vec[:self.EMBEDDING_DIM]
        else:
            # Already a sentence embedding
            return result[:self.EMBEDDING_DIM]
