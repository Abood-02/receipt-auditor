import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Fetching available models for your API key...\n")

for model in client.models.list():
    # Only show models that support generating content (text/multimodal)
    if "generateContent" in model.supported_actions:
        print(f"• Name: {model.name}")