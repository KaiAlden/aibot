from sqlalchemy import DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TCMKnowledge(Base):
    __tablename__ = "tcm_knowledge_documents"
    __table_args__ = (Index("idx_tcm_source", "source"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    translated_text: Mapped[str] = mapped_column(Text, nullable=False)
    document_type: Mapped[str | None] = mapped_column(String(64))
    tags: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), nullable=False)
