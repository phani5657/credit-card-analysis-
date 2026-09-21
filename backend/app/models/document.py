from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime, timezone

from app.db.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer,ForeignKey("users.id"),nullable=False)

    filename = Column(String,nullable=False)

    file_path = Column( String,nullable=False)

    created_at = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))