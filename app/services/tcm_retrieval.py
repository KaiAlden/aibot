from sqlalchemy.orm import Session

from app.repositories.tcm_knowledge import search_tcm_documents
from app.schemas import TCMChunk
from app.services.compliance import filter_medical_advice
from app.services.milvus_tcm import search_tcm_milvus


def retrieve_tcm(db: Session, query: str, top_k: int = 5) -> list[TCMChunk]:
    try:
        milvus_chunks = search_tcm_milvus(query=query, top_k=top_k)
    except Exception:
        milvus_chunks = []
    if milvus_chunks:
        return milvus_chunks

    documents = search_tcm_documents(db, query=query, top_k=top_k)
    chunks: list[TCMChunk] = []
    for document in documents:
        chunks.append(
            TCMChunk(
                text=document.translated_text or document.original_text,
                source=document.source,
                score=1.0,
            )
        )
    return chunks


def build_tcm_answer(query: str, chunks: list[TCMChunk]) -> str:
    if not chunks:
        return "您的问题暂未在当前中医知识库中检索到可靠依据，建议咨询专业中医师。"

    references = "；".join(f"{chunk.text}（来源：{chunk.source}）" for chunk in chunks[:2])
    return filter_medical_advice(f"根据当前知识库，关于“{query}”可参考：{references}")
