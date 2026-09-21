from google import genai
import json

from app.core.config import GEMINI_API_KEY


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def extract_transactions(text: str):

    prompt = f"""
You are extracting credit card transactions from a statement.

Extract only actual individual transactions.

Do NOT extract:
- total amount due
- statement balance
- credit limit
- minimum amount due
- opening balance
- closing balance
- payment due date
- interest charges unless they are clearly individual transactions
- summary totals

For each transaction, return:

- date
- description
- amount
- transaction_type
- category
- merchant name
- payment_method
Date rules:
- Return the date in YYYY-MM-DD format.
- Example: 20 September 2025 → 2025-09-20.
- If the year is not explicitly present, infer it only from the statement period.
- If the date cannot be determined reliably, use null.
Transaction type rules:
- Must be either "debit" or "credit".

Category rules:
Use ONLY one of these categories:

- food
- fuel
- shopping
- entertainment
- travel
- utilities
- emi
- healthcare
- education
- insurance
- fees
- payments
- refunds
- other

If the transaction cannot be confidently assigned to any category above,
always use "other".
Never return null for category.

Payment method rules:
Use ONLY one of these:

- upi
- card
- bank_transfer
- cash
- other

If the payment method cannot be determined from the statement,
always use "other".
Never return null for payment_method.

Merchant name rules:
- merchant_name should be the clean, recognizable name of the
  merchant, shop, company, or service.
- Remove unnecessary transaction IDs, location codes, and bank references.
- Example: "ZOMATO LTD BANGALORE" -> "Zomato".
- Example: "AMAZON PAY INDIA" -> "Amazon".
- Keep the original statement text in description.
- If the merchant cannot be identified clearly, use the original
  description as merchant_name.
- Never return null for merchant_name.

Rules:
- Return ONLY valid JSON.
- Do not include markdown.
- Do not invent transactions.
- amount must be a number.
- date must be in YYYY-MM-DD format or null.
- Use only the allowed category values.
- Use only the allowed payment_method values.
- If a value cannot be determined, use null.

Return a JSON list.

Statement text:

{text}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return json.loads(response.text)