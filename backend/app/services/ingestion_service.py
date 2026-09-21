from sqlalchemy.orm import Session

from app.services.pdf_service import extract_text_from_pdf
from app.services.chunk_service import chunk_pages
from app.services.embedding_service import create_embedding
from app.services.vector_service import store_document_chunk


def process_document(
    db: Session,
    user_id: int,
    document_id: int,
    file_path: str
):

    # Step 1: Extract text page by page
    pages = extract_text_from_pdf(file_path)

    # Step 2: Split pages into chunks
    chunks = chunk_pages(pages)

    stored_chunks = []

    # Step 3: Create embedding for every chunk
    for chunk in chunks:

        embedding = create_embedding(
            chunk["text"]
        )

        # Step 4: Store chunk and embedding
        new_chunk = store_document_chunk(
            db=db,
            user_id=user_id,
            document_id=document_id,
            page_number=chunk["page_number"],
            chunk_number=chunk["chunk_number"],
            content=chunk["text"],
            embedding=embedding
        )

        stored_chunks.append(new_chunk)

    # Step 5: Commit all chunks together
    db.commit()

    return stored_chunks