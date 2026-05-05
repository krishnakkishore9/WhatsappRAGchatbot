import os
import google.generativeai as genai
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

class RAGService:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        # New Pinecone SDK Initialization
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = "txstate-rag-v2"
        
        # Ensure index exists
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        if self.index_name not in existing_indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=384,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        
        self.index = self.pc.Index(self.index_name)

    def get_context(self, query: str, top_k: int = 3) -> str:
        # 1. Generate query embedding with Google Gemini (384 dims)
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=query,
            output_dimensionality=384
        )
        query_embedding = result['embedding']
        
        # 2. Query Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # 3. Aggregate chunks
        context_chunks = [match["metadata"]["text"] for match in results["matches"]]
        return "\n---\n".join(context_chunks)
