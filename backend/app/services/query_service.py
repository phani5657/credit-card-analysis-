from google import genai
import json

from sqlalchemy.orm import Session

from app.services.hybrid_retrieval_service import retrieve_data
from app.services.answer_service import generate_answer

from app.core.config import GEMINI_API_KEY


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def understand_query(question: str):

    prompt = f"""
You are a query planner for a credit card statement analyzer.

Your job is NOT to answer the user's question.

Your job is to analyze the question and create a structured plan
that tells the backend what data should be retrieved.

Available intents:

1. semantic_search
Use for questions about information that may be found in the
statement text.

Examples:
- What does this charge mean?
- What are the fees mentioned in my statement?

2. transaction_filter
Use when the user wants to list, filter, or search transactions.

Examples:
- List transactions above 5000
- Show my transactions from Amazon
- Find all payments above 10000

3. spending_analysis
Use when the user wants insights about their spending.

Examples:
- Where am I spending too much?
- How can I reduce my spending?
- Analyze my spending habits

4. spending_comparison
Use when the user wants to compare spending between time periods.

Examples:
- Compare this year and last year
- Compare January and February

5. document_analysis
Use when the user wants an overview or analysis of a complete statement.

Examples:
- Analyze my statement
- Give me a summary of this statement

6. merchant_analysis
Use when the user asks about spending at a particular merchant.

Examples:
- How much did I spend on Swiggy?
- How much did I spend on Amazon?

Return ONLY valid JSON.

Use exactly this structure:

{{
    "intent": "",
    "data_sources": [],
    "requires_complete_data": false,

    "filters": {{
        "merchant": null,
        "merchants" ; []
        "category": null,
        "categories": [],
        "min_amount": null,
        "max_amount": null
    }},

    "time_scope": "all_time",

    "period": {{
        "month": null,
        "year": null
    }},
    
    "comparison_periods": [],
    "analysis_types": []
    "document_reference": null,

    "limit": null,
    "sort_by": null
}}


Available analysis_types:

1. total_spending
Use when the user wants the total amount spent.

2. category_breakdown
Use when the user wants spending grouped or analyzed by category.

3. merchant_breakdown
Use when the user wants spending grouped or analyzed by merchant.

4. largest_transactions
Use when the user asks for the biggest, highest, or largest expenses.

5. smallest_transactions
Use when the user asks for the smallest expenses.

6. transaction_count
Use when the user wants to know the number of transactions.

7. spending_trend
Use when the user asks about spending patterns or changes over time.

8. period_comparison
Use when the user wants to compare spending between different statements or periods.

9. category_comparison
Use when the user wants to compare categories between different periods.

10. merchant_comparison
Use when the user wants to compare merchant spending between periods.

11. payment_method_breakdown
Use when the user wants spending grouped by payment method.

ANALYSIS RULES:

- For simple transaction searches or transaction lists,
  analysis_types can be empty.

- If the user asks "how much did I spend",
  use total_spending.

- If the user asks about spending by category,
  use category_breakdown.

- If the user asks where they spend the most or too much,
  use:
  - category_breakdown
  - merchant_breakdown
  - largest_transactions

- If the user asks for the biggest or largest expenses,
  use largest_transactions.

- If the user asks for the smallest expenses,
  use smallest_transactions.

- If the user asks how many transactions they made,
  use transaction_count.

- If the user asks about spending patterns or changes over time,
  use spending_trend.

- If the user wants to compare spending between statements
  or time periods:
  - set intent to "spending_comparison"
  - set time_scope to "comparison"
  - use period_comparison
  - fill comparison_periods with the periods mentioned
    in the user's question.

- If the user wants category-wise comparison between periods,
  also use category_comparison.

- If the user wants merchant-wise comparison between periods,
  also use merchant_comparison.

- If the user asks about payment methods,
  use payment_method_breakdown.

- If the user asks how to reduce spending or wants spending
  recommendations, retrieve enough complete transaction data
  and select the relevant analysis_types needed to understand
  the user's spending.

- analysis_types tells the backend what calculations and
  analysis should be performed.

- Do NOT perform calculations yourself.

- Do NOT answer the user's question.
COMPARISON PERIOD RULES:

- comparison_periods should normally contain two periods.

- Each period must use this structure:

  {{
    "month": <month number>,
    "year": <year>
}}

- Example:

  User question:
  "Compare my spending in June 2026 and July 2026"

  Return:

  "time_scope": "comparison",

  "comparison_periods": [
      {{
    "month": 6,
    "year": 2026
}},
      {{
    "month": 7,
    "year": 2026
}}
  ]

- When the user says "compare these two statements",
  set time_scope to "comparison".

- When comparison periods cannot be determined from
  the user's question, leave comparison_periods empty.

- Do not invent months or years.

Rules you should also follow
- data_sources can contain:
  "transactions"
  "rag"
  "documents"

- requires_complete_data should be true when missing data
  could make the answer incorrect.

- time_scope should be one of:
  "latest"
  "all_time"
  "specific_period"
  "comparison"

Additional rules:

- If the user asks for "top" or "largest" transactions,
  use sort_by as "amount_desc".

- If the user asks for the smallest transactions,
  use sort_by as "amount_asc".

- If the user specifies a number of results,
  such as "top 10 transactions",
  set limit to that number.

- If no specific limit is requested,
  use null.
- When the user asks for a total, sum, spending amount,
  analysis, comparison, or any question requiring calculations,
  set requires_complete_data to true.

- Do not set a limit for questions requiring complete
  financial calculations unless the user explicitly asks
  for only a limited number of transactions.
  
  MULTIPLE MERCHANT AND CATEGORY RULES:

MERCHANTS:

- If the user asks about one merchant, use "merchant"
  and keep "merchants" as an empty list.

Example:
"How much did I spend on Swiggy?"

"merchant": "Swiggy"
"merchants": []

- If the user asks about multiple merchants, use
  "merchants" and keep "merchant" as null.

Example:
"How much did I spend on Swiggy and Zomato?"

"merchant": null
"merchants": ["Swiggy", "Zomato"]


CATEGORIES:

- If the user asks about one category, use "category"
  and keep "categories" as an empty list.

Example:
"How much did I spend on food?"

"category": "food"
"categories": []

- If the user asks about multiple categories, use
  "categories" and keep "category" as null.

Example:
"How much did I spend on food and shopping?"

"category": null
"categories": ["food", "shopping"]


- Extract every explicitly requested merchant.
- Extract every explicitly requested category.
- Never put multiple merchants into one string.
- Never put multiple categories into one string.

Do not answer the question.
Do not include markdown.

User question:

{question}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return json.loads(response.text)

def process_query(
    user_id: int,
    question: str,
    db: Session
):

    # Step 1: Understand what the user wants
    query_plan = understand_query(question)

    # Step 2: Retrieve the required data
    retrieved_data = retrieve_data(
        user_id=user_id,
        question=question,
        query_plan=query_plan,
        db=db
    )

    # Step 3: Generate the final answer using the LLM
    answer = generate_answer(
        question=question,
        retrieved_data=retrieved_data
    )

    return {
        "answer": answer,
        "user_id": user_id,
        "query_plan": query_plan
    }