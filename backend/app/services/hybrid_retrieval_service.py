from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.models.transaction import Transaction
from app.services.retrieval_service import retrieve_relevant_chunks
from app.models.document import Document



def get_transactions(
    user_id: int,
    db: Session,
    filters: dict,
    document_ids: list[int],
    time_scope: str,
    period: dict | None = None,
    sort_by: str | None = None,
    limit: int | None = None
):

    query = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == user_id,
            Transaction.document_id.in_(document_ids)
        )
    )
    # Filter transactions by specific month and year
    if time_scope == "specific_period" and period:

        month = period.get("month")
        year = period.get("year")

        if month and year:

            query = query.filter(
                func.extract(
                    "month",
                    Transaction.date
                ) == month,

                func.extract(
                    "year",
                    Transaction.date
                ) == year
            )

    # Filter by merchant
    merchant = filters.get("merchant")

    if merchant:
        query = query.filter(
            or_(
                Transaction.description.ilike(
                    f"%{merchant}%"
                ),
                Transaction.merchant_name.ilike(
                    f"%{merchant}%"
                )
            )
        )
    # Filter by multiple merchants
    merchants = filters.get(
        "merchants",
        []
    )

    if merchants:

        merchant_conditions = []

        for merchant_name in merchants:

            merchant_conditions.append(
                Transaction.description.ilike(
                    f"%{merchant_name}%"
                )
            )

            merchant_conditions.append(
                Transaction.merchant_name.ilike(
                    f"%{merchant_name}%"
                )
            )

        query = query.filter(
            or_(*merchant_conditions)
        )
    # Filter by category
    category = filters.get("category")

    if category:
        query = query.filter(
            Transaction.category.ilike(
                f"%{category}%"
            )
        )
    # Filter by multiple categories
    categories = filters.get(
        "categories",
        []
    )

    if categories:

        category_conditions = []

        for category_name in categories:

            category_conditions.append(
                Transaction.category.ilike(
                    f"%{category_name}%"
                )
            )

        query = query.filter(
            or_(*category_conditions)
        )

    # Filter by minimum amount
    min_amount = filters.get("min_amount")

    if min_amount is not None:
        query = query.filter(
            Transaction.amount >= min_amount
        )

    # Filter by maximum amount
    max_amount = filters.get("max_amount")

    if max_amount is not None:
        query = query.filter(
            Transaction.amount <= max_amount
        )

    # Sort transactions
    if sort_by == "amount_desc":
        query = query.order_by(
            Transaction.amount.desc()
        )

    elif sort_by == "amount_asc":
        query = query.order_by(
            Transaction.amount.asc()
        )

    # Limit number of transactions
    if limit is not None:
        query = query.limit(limit)

    transactions = query.all()

    print("TRANSACTIONS FOUND:", len(transactions))

    return transactions
def get_comparison_transactions(
    user_id: int,
    db: Session,
    filters: dict,
    document_ids: list[int],
    comparison_periods: list[dict],
    documents: list[Document]
):
    # If the user did not specify periods,
    # compare the available documents directly
    if not comparison_periods:

        comparison_data = {}

        for document in documents:

            transactions = (
                db.query(Transaction)
                .filter(
                    Transaction.user_id == user_id,
                    Transaction.document_id == document.id
                )
                .all()
            )

            comparison_data[
                f"document_{document.id}"
            ] = {
                "document_id": document.id,
                "filename": document.filename,
                "transactions": transactions
            }

        return comparison_data
    comparison_data = {}

    for period in comparison_periods:

        month = period.get("month")
        year = period.get("year")

        if not month or not year:
            continue

        transactions = get_transactions(
            user_id=user_id,
            db=db,
            filters=filters,
            document_ids=document_ids,
            time_scope="specific_period",
            period={
                "month": month,
                "year": year
            },
            sort_by=None,
            limit=None
        )

        period_key = f"{year}-{month:02d}"

        comparison_data[period_key] = transactions

    return comparison_data

def get_rag_context(
    user_id: int,
    question: str,
    document_ids: list[int],
    db: Session
):
    chunks = retrieve_relevant_chunks(
        user_id=user_id,
        question=question,
        document_ids=document_ids,
        db=db,
        limit=10
    )

    return chunks

def get_latest_document(
    user_id: int,
    db: Session
):

    document = (
        db.query(Document)
        .filter(
            Document.user_id == user_id
        )
        .order_by(
            Document.created_at.desc()
        )
        .first()
    )

    return document

def retrieve_data(
    user_id: int,
    question: str,
    query_plan: dict,
    db: Session
):

    data_sources = query_plan.get(
        "data_sources",
        []
    )
    sort_by = query_plan.get(
        "sort_by"
    )

    limit = query_plan.get(
        "limit"
)
    filters = query_plan.get(
        "filters",
        {}
    )
    
    time_scope = query_plan.get(
    "time_scope",
    "all_time"
)
    period = query_plan.get(
    "period"
)
    comparison_periods = query_plan.get(
    "comparison_periods",
    []
)
    documents = get_documents_by_scope(
    user_id=user_id,
    db=db,
    time_scope=time_scope
)
    document_ids = [
    document.id
    for document in documents
]

    result = {
        "transactions": [],
        "comparison_transactions": {},
        "rag_chunks": [],
        "documents": documents
    }

    # Retrieve structured transaction data
    if "transactions" in data_sources:

        if time_scope == "comparison":

            result["comparison_transactions"] = (
                        get_comparison_transactions(
                            user_id=user_id,
                            db=db,
                            filters=filters,
                            document_ids=document_ids,
                            comparison_periods=comparison_periods,
                            documents=documents
                        )
            )

        else:

            result["transactions"] = get_transactions(
                user_id=user_id,
                db=db,
                filters=filters,
                document_ids=document_ids,
                time_scope=time_scope,
                period=period,
                sort_by=sort_by,
                limit=limit
            )
    # Retrieve relevant RAG chunks
    if "rag" in data_sources:

        result["rag_chunks"] = get_rag_context(
            user_id=user_id,
            question=question,
            document_ids=document_ids,
            db=db
        )
        


    return result

def get_documents_by_scope(
    user_id: int,
    db: Session,
    time_scope: str
):

    query = (
        db.query(Document)
        .filter(
            Document.user_id == user_id
        )
    )

    # Latest uploaded document
    if time_scope == "latest":

        latest_document = (
            query
            .order_by(Document.created_at.desc())
            .first()
        )

        return [latest_document] if latest_document else []
    elif time_scope == "comparison":

        documents = (
            query
            .order_by(
                Document.created_at.desc()
            )
            .limit(2)
            .all()
        )

        # Older statement first, newer statement second
        return list(reversed(documents))

    # For all other scopes, return all documents.
    # Transaction date filtering will happen separately.
    return (
        query
        .order_by(Document.created_at.asc())
        .all()
    )