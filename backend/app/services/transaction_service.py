from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.document import Document

from app.services.pdf_service import extract_text_from_pdf
from app.services.llm_service import extract_transactions


def process_document_transactions(
    document: Document,
    user_id: int,
    db: Session
):

    # Check if transactions already exist for this document
    existing_transaction = (
        db.query(Transaction)
        .filter(
            Transaction.document_id == document.id
        )
        .first()
    )

    if existing_transaction:
        return []

    # Extract PDF text page by page
    pages = extract_text_from_pdf(
        document.file_path
    )

    saved_transactions = []

    # Process each page
    for page in pages:

        page_text = page["text"]

        # Skip empty pages
        if not page_text.strip():
            continue

        try:
            extracted_transactions = extract_transactions(
                page_text
            )

        except Exception as e:
            print(
                f"Error extracting transactions "
                f"from page {page['page_number']}: {e}"
            )
            continue

        # Process extracted transactions
        for transaction in extracted_transactions:

            # Basic validation
            if transaction.get("amount") is None:
                continue

            if not transaction.get("description"):
                continue

            if transaction.get("transaction_type") not in [
                "debit",
                "credit"
            ]:
                continue
            if not transaction.get("date"):
                continue
            if not transaction.get("merchant_name"):
                continue

            new_transaction = Transaction(
                user_id=user_id,
                document_id=document.id,
                date=transaction.get("date"),
                description=transaction.get("description"),
                amount=transaction.get("amount"),
                transaction_type=transaction.get("transaction_type"),
                category=transaction.get("category"),
                payment_method=transaction.get("payment_method"),
                merchant_name=transaction.get("merchant_name")
)
            
            

            db.add(new_transaction)
            saved_transactions.append(
                new_transaction
            )

    # Save transactions
    db.commit()

    # Refresh database objects
    for transaction in saved_transactions:
        db.refresh(transaction)

    return saved_transactions