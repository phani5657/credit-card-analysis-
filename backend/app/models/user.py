from datetime import datetime, UTC
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped,mapped_column

from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key = True , index = True)

    name: Mapped[str] = mapped_column(String, nullable = False)

    email: Mapped[str] = mapped_column(String,unique = True , nullable = False)

    created_at: Mapped[datetime] = mapped_column(DateTime,default = lambda:datetime.now(UTC), nullable = False)

    password_hash: Mapped[str] = mapped_column(String, nullable=False)