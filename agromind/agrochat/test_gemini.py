import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not set in environment variables")

# Configure Gemini SDK
genai.configure(api_key=api_key)

# Use the valid model
model_name = "models/gemini-flash-latest"

try:
    model = genai.GenerativeModel(model_name)

    # Test prompt
    prompt = "Hello AgroMind! What crops are best for temperate soil?"
    response = model.generate_content(prompt)

    print("--- SUCCESS ---")
    print(response.text)

except Exception as e:
    print("--- AN ERROR OCCURRED ---")
    print(e)
