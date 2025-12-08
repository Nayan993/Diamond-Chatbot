import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("Error: API Key not found in .env")
else:
    print(f"Checking models with new SDK...")
    client = genai.Client(api_key=API_KEY)
    
    try:
        # Just list the models directly without checking attributes
        for model in client.models.list():
            print(f"- Model Name: {model.name}")
            print(f"  Display Name: {model.display_name}")
            print("-" * 30)
            
    except Exception as e:
        print(f"Error listing models: {e}")