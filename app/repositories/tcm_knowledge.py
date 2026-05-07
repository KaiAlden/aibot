from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.knowledge import TCMKnowledge


def search_tcm_documents(db: Session, query: str, top_k: int = 5) -> list[TCMKnowledge]:
    if not query.strip():
        return []

    like_query = f"%{query.strip()}%"
    statement = (
        select(TCMKnowledge)
        .where(
            or_(
                TCMKnowledge.original_text.like(like_query),
                TCMKnowledge.translated_text.like(like_query),
                TCMKnowledge.tags.like(like_query),
            )
        )
        .limit(top_k)
    )
    return list(db.scalars(statement))
