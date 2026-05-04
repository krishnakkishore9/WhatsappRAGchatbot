import asyncio
import os
from services.rag_service import RAGService
from services.llm_manager import LLMManager
from dotenv import load_dotenv

load_dotenv()

async def main():
    print("--- RAG System Test ---")
    
    rag = RAGService()
    llm = LLMManager()
    
    query = "What are the admission requirements for the Master's program?"
    print(f"\nUser Query: {query}")
    
    # 1. Get Context
    print("\nRetrieving context from Pinecone...")
    try:
        context = rag.get_context(query)
        print(f"Context Found (first 200 chars): {context[:200]}...")
    except Exception as e:
        print(f"Error retrieving context: {e}")
        context = "No context available due to error."
    
    # 2. Generate Response
    print("\nGenerating response...")
    response = await llm.generate_response(query, context)
    
    print(f"\nBob's Response:\n{response}")
    print("\n--- Test Complete ---")

if __name__ == "__main__":
    asyncio.run(main())
