from app.models.knowledge import TCMKnowledge
from app.services.milvus_tcm import build_tcm_milvus_rows


def test_build_tcm_milvus_rows_uses_translated_text() -> None:
    document = TCMKnowledge(
        id=1,
        source="测试古籍",
        original_text="古文",
        translated_text="现代文",
        document_type="classic",
        tags="tag",
    )

    rows = build_tcm_milvus_rows([document])

    assert rows[0]["id"] == 1
    assert rows[0]["translated_text"] == "现代文"
    assert len(rows[0]["vector"]) == 1024
