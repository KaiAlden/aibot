from app.services.intent import classify_intent


def test_classify_product_intent_extracts_constraints() -> None:
    result = classify_intent("我是气虚质，推荐100元以内的袋泡茶")

    assert result.intent == "product"
    assert result.constraints["form"] == "茶饮"
    assert result.constraints["price_max"] == 100


def test_classify_tcm_intent() -> None:
    result = classify_intent("阳虚质为什么怕冷")

    assert result.intent == "tcm"


def test_classify_tcm_symptom_keyword() -> None:
    result = classify_intent("白带")

    assert result.intent == "tcm"
