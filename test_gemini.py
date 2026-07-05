import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY")

try:
    genai.configure(api_key=gemini_key)
    valid_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model = genai.GenerativeModel(valid_models[0])
    response = model.generate_content("Say 'Gemini API is working perfectly!'")
    print(response.text)
except Exception as e:
    print(f"Error testing Gemini: {e}")
