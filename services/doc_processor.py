import os
from typing import List
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv(override=True)

class DocumentProcessor:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # New Pinecone SDK Initialization
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = "txstate-rag-openai" # New index for 1536 dimensions
        
        # Create index if it doesn't exist
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        if self.index_name not in existing_indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=1536, # text-embedding-3-small dimension
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        
        self.index = self.pc.Index(self.index_name)
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def extract_text(self, file_path: str) -> str:
        extension = os.path.splitext(file_path)[1].lower()
        if extension == ".pdf":
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        elif extension == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file extension: {extension}")

    def process_and_index(self, file_path: str, document_id: str):
        filename = os.path.basename(file_path)
        text = self.extract_text(file_path)
        chunks = self.text_splitter.split_text(text)
        
        vectors = []
        for i, chunk in enumerate(chunks):
            # Generate embedding with OpenAI
            res = self.openai_client.embeddings.create(input=[chunk], model="text-embedding-3-small")
            embedding = res.data[0].embedding
            
            # Prepare metadata
            metadata = {
                "text": chunk,
                "filename": filename,
                "document_id": document_id,
                "chunk_index": i
            }
            
            vectors.append({
                "id": f"{document_id}_{i}",
                "values": embedding,
                "metadata": metadata
            })
            
            # Batch upsert every 100 vectors
            if len(vectors) >= 100:
                self.index.upsert(vectors=vectors)
                vectors = []
        
        # Final upsert
        if vectors:
            self.index.upsert(vectors=vectors)
        
        return len(chunks)
