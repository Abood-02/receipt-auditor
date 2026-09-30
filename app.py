import os
import time
from typing import List
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError
from pydantic import BaseModel, Field

# 1. Environment & Client Setup
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from your .env file!")

client = genai.Client(api_key=api_key)

# 2. Schemas
class LineItem(BaseModel):
    description: str = Field(description="Name or description of the product/service")
    quantity: int = Field(description="Number of units purchased")
    price: float = Field(description="Total price for this line item")

class ReceiptData(BaseModel):
    vendor: str = Field(description="Name of the business or vendor")
    date: str = Field(description="Date of the transaction in YYYY-MM-DD format")
    items: List[LineItem] = Field(description="List of all purchased items")
    subtotal: float = Field(description="Subtotal amount before tax")
    tax: float = Field(description="Tax amount")
    total: float = Field(description="Total final amount paid")
    category: str = Field(description="Expense category: Meals, Travel, Supplies, or Other")

# 3. Audit Function (Pure Python logic)
def audit_receipt(receipt: ReceiptData, meal_limit: float = 8.00) -> List[str]:
    flags = []
    tolerance = 0.05  # Allow minor rounding differences (5 cents)

    # Check 1: Do line items sum up to the subtotal?
    calculated_subtotal = sum(item.price for item in receipt.items)
    if abs(calculated_subtotal - receipt.subtotal) > tolerance:
        flags.append(
            f"MATH_MISMATCH: Items sum to {calculated_subtotal:.2f}, but subtotal says {receipt.subtotal:.2f}"
        )

    # Check 2: Does subtotal + tax equal total?
    calculated_total = receipt.subtotal + receipt.tax
    if abs(calculated_total - receipt.total) > tolerance:
        flags.append(
            f"MATH_MISMATCH: Subtotal + tax is {calculated_total:.2f}, but total says {receipt.total:.2f}"
        )

    # Check 3: Meal policy limit check
    if receipt.category == "Meals" and receipt.total > meal_limit:
        flags.append(
            f"POLICY_VIOLATION: Meal expense of ${receipt.total:.2f} exceeds policy limit of ${meal_limit:.2f}"
        )

    return flags

# 4. Receipt Input
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

# 5. Extract with Retry
print("Calling Gemini model...")
response = None
for attempt in range(3):
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=f"Extract receipt data from this text:\n{raw_receipt_text}",
            config={
                "response_mime_type": "application/json",
                "response_schema": ReceiptData,
            },
        )
        break
    except ServerError as e:
        print(f"Server busy (attempt {attempt + 1}/3). Retrying in 15 seconds...")
        time.sleep(15)
    except Exception as e:
        print(f"Unexpected error: {e}")
        break

if response:
    # Validate with Pydantic
    receipt = ReceiptData.model_validate_json(response.text)
    
    print("\n--- EXTRACTED RECEIPT OBJECT ---")
    print(f"Vendor:   {receipt.vendor}")
    print(f"Date:     {receipt.date}")
    print(f"Category: {receipt.category}")
    print(f"Total:    ${receipt.total:.2f}")
    print(f"Items ({len(receipt.items)}):")
    for item in receipt.items:
        print(f"  - {item.quantity}x {item.description} (${item.price:.2f})")

    # Run the audit
    flags = audit_receipt(receipt, meal_limit=8.00)

    print("\n--- AUDIT RESULTS ---")
    if flags:
        print("⚠️ AUDIT FLAGS DETECTED:")
        for flag in flags:
            print(f"  • {flag}")
    else:
        print("✅ Clean receipt! No audit flags.")
else:
    print("❌ Failed to receive a response from Gemini.")