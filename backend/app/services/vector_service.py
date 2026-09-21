from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk


def store_document_chunk(
    db: Session,
    user_id: int,
    document_id: int,
    page_number: int,
    chunk_number: int,
    content: str,
    embedding: list[float]
):

    new_chunk = DocumentChunk(
        user_id=user_id,
        document_id=document_id,
        page_number=page_number,
        chunk_number=chunk_number,
        content=content,
        embedding=embedding
    )

    db.add(new_chunk)

    return new_chunk