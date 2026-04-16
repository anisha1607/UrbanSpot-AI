import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=API_KEY)

print("Available Models:")
try:
    for model in client.models.list():
        if "generateContent" in model.supported_actions: # Correct field name
            print(f"- {model.name}")
except Exception as e:
    print(f"Error listing models: {e}")
