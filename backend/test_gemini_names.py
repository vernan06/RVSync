import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

models_to_try = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-pro"]

for model_name in models_to_try:
    print(f"Testing model: {model_name}...")
    try:
        model = genai.GenerativeModel(model_name=model_name)
        response = model.generate_content("Hello")
        print(f"✅ Success with {model_name}: {response.text[:20]}...")
        break
    except Exception as e:
        print(f"❌ Failed with {model_name}: {e}")
