import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from app import get_gemini_model

load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY")

prompt = 'Return a valid JSON object with a single key "slogan" containing a 5-word slogan for AI marketing.'
print("Testing Gemini directly...")
try:
    genai.configure(api_key=gemini_key)
    model = get_gemini_model()
    print(f"Model used: {model.model_name}")
    response = model.generate_content(prompt)
    text = response.text.strip()
    print(f"Raw Response: {text}")
    if text.startswith('```json'): text = text[7:-3]
    elif text.startswith('```'): text = text[3:-3]
    print(f"Cleaned Text: {text}")
    parsed = json.loads(text.strip())
    print(f"Parsed JSON Result: {parsed}")
except Exception as e:
    import traceback
    traceback.print_exc()
