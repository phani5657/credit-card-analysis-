from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import create_embedding


def retrieve_relevant_chunks(
    db: Session,
    user_id: int,
    question: str,
    document_ids: list[int],
    limit: int = 10
):

    # Convert the user's question into an embedding
    question_embedding = create_embedding(question)

    # Search only the current user's chunks
    # Order chunks by cosine similarity
    chunks = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.user_id == user_id,
            DocumentChunk.document_id.in_(document_ids)
        )
        .order_by(
            DocumentChunk.embedding.cosine_distance(
                question_embedding
            )
        )
        .limit(limit)
        .all()
    )

    return chunks


def retrieve_document_chunks(
    db: Session,
    user_id: int,
    document_id: int
):

    # Retrieve all chunks belonging to a particular document
    # and make sure the document belongs to the current user
    chunks = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.user_id == user_id,
            DocumentChunk.document_id == document_id
        )
        .order_by(
            DocumentChunk.page_number,
            DocumentChunk.chunk_number
        )
        .all()
    )

    return chunks

