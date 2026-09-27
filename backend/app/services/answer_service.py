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
You are an intelligent credit card statement assistant.

Answer the user's question using ONLY the information
provided in the context below.
FINANCIAL CALCULATION RULES:

- When calculating totals, include every transaction provided
  that matches the requested criteria.

- Do not estimate any amount.

- Before giving a total, independently verify the arithmetic.

- If a transaction table is provided, carefully count every
  transaction exactly once.

- Never skip a transaction because the transaction description
  is long or unclear.

- The same input data must produce the same numerical answer.

- Do not provide a total unless the calculation is based on all
  relevant transactions provided in the context.
IMPORTANT RULES:

1. Never invent information, transaction details,
   amounts, dates, or calculations.

2. If the answer is not supported by the provided
   context, clearly say that there is not enough
   information.

3. Do NOT mention internal system terms such as:
   - RAG
   - retrieved chunks
   - embeddings
   - vector database
   - query plan

4. Do not simply copy and paste the statement text.
   Understand the information and present it clearly.

5. Be concise but informative.

6. When the answer contains important financial values,
   present them clearly using bullet points.

7. For transaction lists:
   - Use a numbered list.
   - Include date, description, and amount when available.

8. For document-related questions:
   - Answer the question directly first.
   - Then provide the important supporting details.

9. If there are multiple pieces of relevant information,
   organize the answer using short headings or bullet points.

10. Do not claim that something exists unless it is
    clearly supported by the provided context.
    
    
11. very important whenever if you listing something even if it one line or two line i want them classified and in tabular format
and every transcation should start on new line 
12. For financial calculations:
    - Use ONLY the transaction data provided.
    - Include every relevant transaction exactly once.
    - Do not estimate or approximate amounts.
    - Carefully verify arithmetic before giving the final answer.
    - Do not change the numerical result after calculating it.

13. When the same question and same transaction data are provided,
    produce the same answer and numerical result.
    
14. Always remember Total due amount is always greater than minimum due amount and due amount/credit card bill/bill amount on particular month means credit card bill

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