from app.schemas import Constitution
from app.services.symptom_matcher import match_constitution


def test_match_constitution_high_confidence() -> None:
    result = match_constitution("我最近怕冷，手脚冰凉，还总是腰膝发冷")

    assert result.constitution == Constitution.yangxu
    assert result.confidence >= 0.82
    assert result.need_followup is False


def test_match_constitution_mid_confidence_needs_followup() -> None:
    result = match_constitution("我最近有点怕冷，也喜欢喝热水")

    assert result.constitution == Constitution.yangxu
    assert 0.65 <= result.confidence < 0.82
    assert result.need_followup is True
    assert result.followup_question


def test_match_constitution_low_confidence_fallback() -> None:
    result = match_constitution("今天想看看有什么商品")

    assert result.constitution is None
    assert result.confidence < 0.65
    assert result.need_followup is True
