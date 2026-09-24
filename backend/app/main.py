from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine

from app.models.user import User
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.transaction import Transaction

from app.api.user import router as user_router
from app.api.document import router as document_router
from app.api.query import router as query_router


app = FastAPI()


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://credit-card-analysis-1.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# ROUTERS
# ==========================================

app.include_router(user_router)
app.include_router(document_router)
app.include_router(query_router)


# ==========================================
# DATABASE
# ==========================================

Base.metadata.create_all(bind=engine)


# ==========================================
# BASIC ROUTES
# ==========================================

@app.get("/")
def home():
    return {
        "message": "Credit Card Analyzer API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }