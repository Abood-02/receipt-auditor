import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Messy raw receipt data (typical OCR output)
raw_receipt_text = """
*** COFFEE ROASTERS INC ***
Store #402 - Amman, Jordan
Date: 2026-09-15 08:42 AM

1x Oat Latte         3.50
2x Croissant         4.00
1x Bottled Water     1.00

SUBTOTAL: 8.50
TAX (16%): 1.36
TOTAL: 9.86

Thank you for visiting!
Card ending in 4421
"""

prompt = f"""
Extract the vendor, date, line items, and total amount from this receipt text:

{raw_receipt_text}
"""

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=prompt,
)

print("--- RAW MODEL OUTPUT ---")
print(response.text)