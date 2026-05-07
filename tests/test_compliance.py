from app.services.compliance import SAFE_MEDICAL_FALLBACK, filter_medical_advice


def test_filter_medical_advice_blocks_decoction_instruction() -> None:
    assert filter_medical_advice("配方：大黄三钱。用水煎服。") == SAFE_MEDICAL_FALLBACK


def test_filter_medical_advice_blocks_powder_instruction() -> None:
    assert filter_medical_advice("用人参煎汤，冲服药末。") == SAFE_MEDICAL_FALLBACK


def test_filter_medical_advice_allows_general_care() -> None:
    text = "阳虚者常见怕冷，应注意保暖。"

    assert filter_medical_advice(text) == text
