from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.document import Document
from app.core.security import get_current_user
from app.schemas.document import DocumentResponse

from app.services.pdf_service import extract_text_from_pdf
from app.services.ingestion_service import process_document
from app.models.document_chunk import DocumentChunk
from app.services.transaction_service import process_document_transactions

import os
import shutil
import uuid

router = APIRouter(prefix="/documents",tags=["documents"])


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),current_user_id: int = Depends(get_current_user),db: Session = Depends(get_db)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400,detail="Only PDF files are allowed" )

    upload_folder = "uploads"

    os.makedirs( upload_folder, exist_ok=True)

    unique_filename = f"{uuid.uuid4()}_{file.filename}"

    file_path = os.path.join(upload_folder,unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    new_document = Document( user_id=current_user_id,filename=file.filename,file_path=file_path)
    db.add(new_document)
    db.commit()
    db.refresh(new_document)

        # Process PDF and create chunks + embeddings
    stored_chunks = process_document(
        db=db,
        user_id=current_user_id,
        document_id=new_document.id,
        file_path=new_document.file_path
    )


    # Extract and store transactions
    saved_transactions = process_document_transactions(
        document=new_document,
        user_id=current_user_id,
        db=db
    )


    return {
        "message": "File uploaded and processed successfully",
        "document_id": new_document.id,
        "filename": file.filename,
        "chunks_created": len(stored_chunks),
        "transactions_created": len(saved_transactions)
    }

@router.get("/",response_model=list[DocumentResponse])
def get_my_documents(current_user_id: int = Depends(get_current_user),db: Session = Depends(get_db)):

    documents = db.query(Document).filter( Document.user_id == current_user_id).all()

    return documents


@router.get("/{document_id}",response_model=DocumentResponse)
def get_document(document_id: int,current_user_id: int = Depends(get_current_user),db: Session = Depends(get_db)):

    document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user_id).first()

    if not document:
        raise HTTPException(status_code=404,detail="Document not found")

    return document

@router.delete("/{document_id}")
def delete_document(document_id: int,current_user_id: int = Depends(get_current_user),db: Session = Depends(get_db)):

    document = db.query(Document).filter( Document.id == document_id, Document.user_id == current_user_id).first()

    if not document:
        raise HTTPException(status_code=404,detail="Document not found")

    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully"
    }

@router.post("/{document_id}/process")
def process_uploaded_document(
    document_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Find the document and verify ownership
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # Check if the document was already processed
    existing_chunk = db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id
    ).first()

    if existing_chunk:
        raise HTTPException(
            status_code=400,
            detail="Document has already been processed"
        )

    # Process PDF and store chunks + embeddings
    stored_chunks = process_document(
        db=db,
        user_id=current_user_id,
        document_id=document.id,
        file_path=document.file_path
    )
    saved_transactions = process_document_transactions(
    document=document,
    user_id=current_user_id,
    db=db)
    return {
        "message": "Document processed successfully",
        "document_id": document.id,
        "chunks_created": len(stored_chunks),
        "transactions_created": len(saved_transactions)
} 