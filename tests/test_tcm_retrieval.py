from app.schemas import TCMChunk
from app.services.tcm_retrieval import build_tcm_answer


def test_build_tcm_answer_fallback_when_no_chunks() -> None:
    answer = build_tcm_answer("为什么怕冷", [])

    assert "暂未" in answer


def test_build_tcm_answer_uses_sources() -> None:
    answer = build_tcm_answer(
        "为什么怕冷",
        [TCMChunk(text="阳气不足则易畏寒。", source="测试古籍", score=1.0)],
    )

    assert "阳气不足" in answer
    assert "测试古籍" in answer
