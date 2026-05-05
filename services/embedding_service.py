import os
from fastembed import TextEmbedding
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
    """
    Generates 384-dimensional text embeddings using FastEmbed.
    Uses BAAI/bge-small-en-v1.5 via ONNX runtime.
    No PyTorch, no API keys, no quotas. Works within 512MB RAM.
    """

    MODEL_NAME = "BAAI/bge-small-en-v1.5"  # 384 dims, ~90MB ONNX model
    EMBEDDING_DIM = 384

    def __init__(self):
        print(f"EmbeddingService: Loading '{self.MODEL_NAME}' via FastEmbed...")
        self.model = TextEmbedding(model_name=self.MODEL_NAME)
        print("EmbeddingService: Model ready.")

    def embed(self, text: str) -> list:
        """Returns a 384-dimensional embedding vector."""
        embeddings = list(self.model.embed([text]))
        return embeddings[0].tolist()
