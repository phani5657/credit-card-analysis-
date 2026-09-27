from google import genai

from app.core.config import GEMINI_API_KEY


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def generate_answer(
    question: str,
    retrieved_data: dict
):

    transactions = retrieved_data.get(
        "transactions",
        []
    )

    rag_chunks = retrieved_data.get(
        "rag_chunks",
        []
    )

    documents = retrieved_data.get(
        "documents", []
    )

    # -----------------------------------
    # FORMAT TRANSACTION DATA
    # -----------------------------------

    transactions_context = ""

    if transactions:

        transactions_context = "TRANSACTIONS:\n\n"

        for index, transaction in enumerate(
            transactions,
            start=1
        ):

            transactions_context += (
                f"Date: {transaction.date}, "
                f"Description: {transaction.description}, "
                f"Amount: {transaction.amount}, "
                f"Type: {transaction.transaction_type}, "
                f"Category: {transaction.category}, "
                f"Payment Method: {transaction.payment_method}\n"
            )
    else:

        transactions_context = (
            "No transaction data was retrieved.\n"
        )


    # -----------------------------------
    # FORMAT RAG CONTEXT
    # -----------------------------------

    rag_context = ""

    if rag_chunks:

        rag_context = (
            "RELEVANT STATEMENT INFORMATION:\n\n"
        )

        for index, chunk in enumerate(
            rag_chunks,
            start=1
        ):

            rag_context += (
                f"[Source {index} | "
                f"Page {chunk.page_number}]\n"
                f"{chunk.content}\n\n"
            )

    else:

        rag_context = (
            "No relevant statement content was retrieved.\n"
        )


    # -----------------------------------
    # DOCUMENT INFORMATION
    # -----------------------------------
    document_context = ""

    if documents:

        document_context = "DOCUMENTS:\n\n"

        for index, document in enumerate(
            documents,
            start=1
        ):

            document_context += (
                f"Document {index}:\n"
                f"ID: {document.id}\n"
                f"Filename: {document.filename}\n\n"
            )

    else:

        document_context = (
            "No document information available.\n"
        )

    # -----------------------------------
    # ANSWER PROMPT
    # -----------------------------------

    prompt = f"""
YYou are an intelligent credit card statement assistant.

Answer the user's question using ONLY the information provided in the context.

IMPORTANT RULES:

1. Never invent or estimate information. If the answer is not supported by the
context, say there is not enough information.

2. For financial calculations:
- Use only the provided transaction data.
- Include every relevant transaction exactly once.
- Verify the arithmetic before answering.
- Never change the calculated result.

3. CREDIT CARD FIELD DEFINITIONS:
- Total Amount Due = the total credit card bill for the statement.
- Minimum Amount Due = the minimum payment required for the statement.
- Payment Due Date = the date by which payment is due.
- Statement Period = the period covered by the statement.

4. NEVER confuse Total Amount Due with Minimum Amount Due.
Always use the value associated with the exact label in the statement.
Do not swap values based on which amount is larger or smaller.

5. When the user says:
- "credit card bill"
- "bill amount"
- "total bill"
- "total due"
- "what do I owe"

interpret it as Total Amount Due unless the user specifically asks for
Minimum Amount Due.

6. If the user asks for Minimum Amount Due, return ONLY the value associated
with the "Minimum Amount Due" / "Minimum Payment Due" field.

7. Do not confuse these fields with Previous Balance, Current Balance,
Statement Balance, Credit Limit, Available Credit, Payments, or transaction
amounts.

8. Whenever listing multiple items, ALWAYS use a TABLE.
Every transaction must have its own row and must include the date, description,
and amount when available.

9. Be concise and answer the question directly first.

10. Do not mention internal terms such as RAG, embeddings, vector database,
retrieved chunks, or query plans.

FINAL CHECK BEFORE ANSWERING:
- Did I identify the exact field requested?
- Did I use the value associated with that field's label?
- Did I include every relevant transaction?
- Did I verify any calculation?
USER QUESTION:
{question}


{transactions_context}


{document_context}


{rag_context}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    config={
        "temperature": 0
    }
    )

    return response.text