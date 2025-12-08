# backend/llm.py
import os
from google import genai
from typing import List
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Debug: Print to verify the key is loaded
print(f"API Key loaded: {GEMINI_API_KEY[:20] if GEMINI_API_KEY else 'None'}...")
print(f"API Key length: {len(GEMINI_API_KEY) if GEMINI_API_KEY else 0}")
print(f"Model: {GEMINI_MODEL}")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

def ask_gemini(question: str, context_chunks: List[str]) -> str:
    """
    Sends a question along with context to Gemini LLM and returns the answer.
    """
    if not context_chunks:
        return "No context available to answer the question."
    
    context_text = "\n".join(context_chunks)
    
    prompt = f"""Answer the question strictly based on the provided context below.
Do not add any information not in the context.

Context:
{context_text}

Question:
{question}

Answer:"""
    
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        
        # Handle response properly
        if hasattr(response, 'text'):
            return response.text
        elif hasattr(response, 'candidates') and response.candidates:
            return response.candidates[0].content.parts[0].text
        else:
            return "Gemini returned no answer."
            
    except Exception as e:
        return f"Error connecting to Gemini API: {e}"