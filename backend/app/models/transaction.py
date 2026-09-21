from datetime import date, datetime, UTC

from sqlalchemy import (
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,Date

)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("documents.id"),
        nullable=False
    )

    date: Mapped[Date] = mapped_column(
        Date,
        nullable=False
    )
    merchant_name: Mapped[str] = mapped_column(
    String,
    nullable=False
    )

    description: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    transaction_type: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    category: Mapped[str ] = mapped_column(
        String,
        nullable=False
    )

    payment_method: Mapped[str ] = mapped_column(
        String,
        nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    
