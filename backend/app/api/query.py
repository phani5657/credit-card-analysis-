from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.query_service import process_query
from app.core.security import get_current_user


router = APIRouter(
    prefix="/query",
    tags=["Query"]
)


class QueryRequest(BaseModel):
    question: str


@router.post("/")
def ask_question(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):

    result = process_query(
        question=request.question,
        user_id=current_user,
        db=db
    )

    return result