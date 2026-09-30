# Smart Receipt & Expense Auditor

A Python pipeline that ingests unstructured receipt text, extracts strictly validated financial schemas using Google Gemini structured outputs, and runs programmatic auditing logic to catch math discrepancies and company policy violations.

## Features
- **Structured Schema Extraction:** Enforces strict Pydantic schemas (`ReceiptData`, `LineItem`) directly via Gemini API.
- **Categorization:** Automatically classifies expenses (Meals, Travel, Supplies, etc.).
- **Deterministic Auditing:** 
  - Verifies line item sum matches receipt subtotal.
  - Verifies subtotal + tax matches final total.
  - Flags expenses exceeding custom policy thresholds.
- **Resilient Requests:** Implements retry handling for transient server spikes.

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/](https://github.com/)<your-username>/receipt-auditor.git
   cd receipt-auditor