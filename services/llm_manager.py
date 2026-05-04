import os
import httpx
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

class LLMManager:
    def __init__(self):
        # Load and sanitize keys
        openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        hf_key = os.getenv("HF_API_KEY", "").strip()
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        
        # Diagnostic Check (Safe logging)
        print(f"--- API Key Health Check ---")
        print(f"OpenAI Key: {'Loaded' if openai_key else 'MISSING'} (Len: {len(openai_key)})")
        print(f"HF Key: {'Loaded' if hf_key else 'MISSING'} (Len: {len(hf_key)})")
        print(f"Gemini Key: {'Loaded' if gemini_key else 'MISSING'} (Len: {len(gemini_key)})")
        print(f"----------------------------")

        # Primary: OpenAI
        self.openai_client = OpenAI(api_key=openai_key)
        
        # Secondary: HF Chain
        self.hf_api_key = hf_key
        self.hf_models = [
            "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "meta-llama/Meta-Llama-3.1-70B-Instruct",
            "mistralai/Mistral-7B-Instruct-v0.2",
            "distilgpt2"
        ]
        
        # Tertiary: Gemini (Using Official SDK with Discovery)
        if gemini_key:
            try:
                genai.configure(api_key=gemini_key)
                # Let's see what models you actually have access to
                print("Checking available Gemini models...")
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                print(f"Available Models: {available_models[:5]}...") # Show first 5
                
                # Pick the first flash or pro model available
                self.gemini_model_name = next((m for m in available_models if 'flash' in m), 
                                         next((m for m in available_models if 'pro' in m), 
                                         available_models[0] if available_models else "gemini-1.5-flash"))
                
                print(f"Selected Gemini Model: {self.gemini_model_name}")
                self.gemini_model = genai.GenerativeModel(self.gemini_model_name)
            except Exception as e:
                print(f"Gemini Discovery Failed: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None
        
        self.system_prompt = (
            "You are Bob, the Texas State University Admission Assistant. "
            "Use the provided context to answer the user's question accurately. "
            "If the answer is not in the context, say: 'I\'m sorry, I don\'t have that information. "
            "Please contact the Admissions Office at 9704574919 or test@gmail.com for further assistance.' "
            "Keep your tone helpful, professional, and friendly."
        )

    async def generate_response(self, query: str, context: str) -> str:
        prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
        
        # Try OpenAI first
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI failed: {e}. Starting Hugging Face Fallback Chain...")
            
            # Try each Hugging Face model in the list
            for model_id in self.hf_models:
                print(f"Trying HF Model: {model_id}...")
                hf_res = await self._call_huggingface(query, context, model_id)
                if hf_res and not hf_res.startswith("Error:"):
                    print(f"Success with HF Model: {model_id}!")
                    return hf_res
                print(f"HF Model {model_id} failed: {hf_res}")
            
            # If all HF models fail, try Gemini
            print("All HF models failed. Falling back to Gemini...")
            return await self._call_gemini(query, context)

    async def _call_huggingface(self, query: str, context: str, model_id: str) -> str:
        """
        Calls a specific Hugging Face model using the Inference API.
        """
        if not self.hf_api_key:
            return "Error: No HF key"
        
        api_url = f"https://api-inference.huggingface.co/models/{model_id}"
        headers = {"Authorization": f"Bearer {self.hf_api_key}"}
        
        # Determine prompt format based on model type
        if "mistral" in model_id.lower() or "zephyr" in model_id.lower():
            prompt = f"<s>[INST] {self.system_prompt}\n\nContext: {context}\n\nQuestion: {query} [/INST]"
        elif "llama" in model_id.lower():
            prompt = f"[INST] <<SYS>>\n{self.system_prompt}\n<</SYS>>\n\nContext: {context}\n\nQuestion: {query} [/INST]"
        else:
            prompt = f"{self.system_prompt}\n\nContext: {context}\n\nQuestion: {query}\n\nAnswer:"
        
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 500, "temperature": 0.3}
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(api_url, headers=headers, json=payload, timeout=30.0)
                if response.status_code != 200:
                    return f"Error: {response.status_code}"
                
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0]["generated_text"].split("<|assistant|>")[-1].strip()
                return "Error: Format"
            except:
                return "Error: Request"

    async def _call_gemini(self, query: str, context: str) -> str:
        """
        Final fail-safe using the official Google Gemini SDK.
        """
        if not self.gemini_model:
            return "Error: No Gemini SDK configured"
        
        try:
            prompt = f"{self.system_prompt}\n\nContext: {context}\n\nQuestion: {query}"
            # SDK handles the version and endpoint selection automatically
            response = self.gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error: Gemini SDK failed. Detail: {str(e)}"
