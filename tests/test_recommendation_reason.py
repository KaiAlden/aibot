from app.schemas import Constitution, ProductCandidate, TCMChunk
from app.services.recommendation_reason import build_product_reason


def test_build_product_reason_uses_description_and_source() -> None:
    reason = build_product_reason(
        ProductCandidate(id=1, name="黄芪茶", description="补气"),
        Constitution.qixu,
        [TCMChunk(text="气虚常见疲乏。", source="九体质文档", score=1.0)],
    )

    assert "补气" in reason
    assert "九体质文档" in reason
    assert "不替代专业诊疗" in reason


def test_build_product_reason_skips_sensitive_chunks() -> None:
    reason = build_product_reason(
        ProductCandidate(id=1, name="黄芪茶", description="补气"),
        Constitution.qixu,
        [TCMChunk(text="配方：黄芪三钱，用水煎服。", source="古籍", score=1.0)],
    )

    assert "古籍中的相关养生理论" not in reason
    assert "未找到可安全引用" in reason
