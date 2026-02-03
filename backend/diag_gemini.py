import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"Using API Key: {api_key[:10]}...")

try:
    genai.configure(api_key=api_key)
    print("Attempting to list models...")
    models = genai.list_models()
    for m in models:
        print(f"Model found: {m.name} | Methods: {m.supported_generation_methods}")
except Exception as e:
    print(f"Caught Error: {e}")
